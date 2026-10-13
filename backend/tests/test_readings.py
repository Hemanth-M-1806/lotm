import os
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "postgresql+psycopg://lotm_user:secret@localhost:5432/lotm_tarot"
os.environ["SECRET_KEY"] = "supersecretkeythatislongerthanthirtytwochars"

from app.core.database import get_db_session
from app.core.security import create_access_token
from app.main import app
from app.models.card import TarotCard
from app.models.reading import Reading, ReadingCard
from app.models.user import User
from app.schemas.reading import SPREAD_CONFIG, ReadingCreate, SpreadType
from app.services.reading_service import (
    _fisher_yates_sample,
    synthesize_interpretation,
)


class TestReadingDomainAndService(unittest.TestCase):
    def setUp(self):
        self.mock_cards = [
            TarotCard(
                id=i,
                name=f"Card {i}",
                arcana_type="major",
                card_number=i,
                upright_meaning=f"Upright meaning {i}",
                reversed_meaning=f"Reversed meaning {i}",
                mystical_lore=f"Lore {i}",
            )
            for i in range(22)
        ]

    def test_fisher_yates_sample_unique_without_replacement(self):
        sampled = _fisher_yates_sample(self.mock_cards, 3)
        self.assertEqual(len(sampled), 3)
        sampled_ids = [c.id for c in sampled]
        self.assertEqual(len(set(sampled_ids)), 3)

    def test_fisher_yates_sample_full_deck(self):
        sampled = _fisher_yates_sample(self.mock_cards, 22)
        self.assertEqual(len(sampled), 22)
        self.assertEqual(len(set(c.id for c in sampled)), 22)

    def test_synthesize_interpretation(self):
        items = [
            {
                "card": self.mock_cards[0],
                "position_name": "Past",
                "is_reversed": False,
            },
            {
                "card": self.mock_cards[1],
                "position_name": "Present",
                "is_reversed": True,
            },
        ]
        text = synthesize_interpretation(
            spread_type=SpreadType.THREE_CARD,
            cards_with_meta=items,
            question="Will the Tarot Club succeed?",
        )
        self.assertIn("Will the Tarot Club succeed?", text)
        self.assertIn("Upright meaning 0", text)
        self.assertIn("Reversed meaning 1", text)
        self.assertIn("[Past] Card 0 (Upright)", text)
        self.assertIn("[Present] Card 1 (Reversed)", text)


class TestReadingAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.user_id = uuid.uuid4()
        self.token = create_access_token(subject=str(self.user_id))
        self.mock_user = User(
            id=self.user_id,
            username="klein_moretti",
            email="klein@backlund.mysteries",
            display_name="The Fool",
            password_hash="fakehash",
            email_verified=True,
            created_at=datetime.now(timezone.utc),
        )
        self.mock_cards = [
            TarotCard(
                id=i,
                name=f"Major Arcana {i}",
                arcana_type="major",
                card_number=i,
                upright_meaning=f"Upright meaning {i}",
                reversed_meaning=f"Reversed meaning {i}",
            )
            for i in range(22)
        ]

    def test_create_reading_guest(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_session.add = MagicMock()
            mock_cards_res = MagicMock()
            mock_cards_res.scalars.return_value.all.return_value = self.mock_cards
            mock_session.execute.return_value = mock_cards_res
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/readings",
                json={
                    "spread_type": "three_card",
                    "question": "What does the fog conceal?",
                },
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertEqual(data["spread_type"], "three_card")
            self.assertEqual(data["question"], "What does the fog conceal?")
            self.assertIsNone(data["user_id"])
            self.assertEqual(len(data["cards"]), 3)
            self.assertIn("Past / Cause", [c["position_name"] for c in data["cards"]])
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_create_reading_authenticated(self):
        async def override_db():
            mock_session = AsyncMock()
            mock_session.add = MagicMock()
            # First query is User lookup for get_optional_current_user
            mock_user_res = MagicMock()
            mock_user_res.scalar_one_or_none.return_value = self.mock_user

            # Second query is TarotCard pool
            mock_cards_res = MagicMock()
            mock_cards_res.scalars.return_value.all.return_value = self.mock_cards

            mock_session.execute.side_effect = [mock_user_res, mock_cards_res]
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.post(
                "/api/v1/readings",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "spread_type": "single_card",
                    "question": "Daily guidance",
                },
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertEqual(data["user_id"], str(self.user_id))
            self.assertEqual(len(data["cards"]), 1)
            self.assertEqual(data["cards"][0]["position_name"], "Guidance")
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_create_reading_invalid_spread_type_fails(self):
        res = self.client.post(
            "/api/v1/readings",
            json={"spread_type": "unsupported_spread"},
        )
        self.assertEqual(res.status_code, 422)

    def test_list_readings_unauthorized_without_token(self):
        res = self.client.get("/api/v1/readings")
        self.assertEqual(res.status_code, 401)

    def test_list_readings_paginated_success(self):
        now = datetime.now(timezone.utc)
        mock_reading = Reading(
            id=uuid.uuid4(),
            user_id=self.user_id,
            spread_type="three_card",
            question="Divination test",
            interpretation="Interpretation text",
            is_favorite=False,
            created_at=now,
            cards=[],
        )

        async def override_db():
            mock_session = AsyncMock()
            # 1. User lookup
            user_res = MagicMock()
            user_res.scalar_one_or_none.return_value = self.mock_user

            # 2. Count query
            count_res = MagicMock()
            count_res.scalar_one.return_value = 1

            # 3. Readings list query
            readings_res = MagicMock()
            readings_res.scalars.return_value.all.return_value = [mock_reading]

            mock_session.execute.side_effect = [user_res, count_res, readings_res]
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.get(
                "/api/v1/readings?page=1&page_size=10",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["total"], 1)
            self.assertEqual(data["page"], 1)
            self.assertEqual(data["page_size"], 10)
            self.assertEqual(len(data["items"]), 1)
            self.assertEqual(data["items"][0]["id"], str(mock_reading.id))
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_get_reading_by_id_anti_idor_defense(self):
        # Reading belongs to another user
        other_user_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        foreign_reading = Reading(
            id=uuid.uuid4(),
            user_id=other_user_id,
            spread_type="single_card",
            question="Private question",
            interpretation="Secret",
            is_favorite=False,
            created_at=now,
            cards=[],
        )

        async def override_db():
            mock_session = AsyncMock()
            # 1. User auth lookup
            user_res = MagicMock()
            user_res.scalar_one_or_none.return_value = self.mock_user

            # 2. Reading lookup
            reading_res = MagicMock()
            reading_res.scalar_one_or_none.return_value = foreign_reading

            mock_session.execute.side_effect = [user_res, reading_res]
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.get(
                f"/api/v1/readings/{foreign_reading.id}",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            # Must return 404 to avoid enumerating existence of other users' readings
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res.json()["error"]["code"], "NOT_FOUND")
        finally:
            app.dependency_overrides.pop(get_db_session, None)

    def test_toggle_favorite_reading_success(self):
        now = datetime.now(timezone.utc)
        my_reading = Reading(
            id=uuid.uuid4(),
            user_id=self.user_id,
            spread_type="three_card",
            question="Favorite reading",
            interpretation="Insightful",
            is_favorite=False,
            created_at=now,
            cards=[],
        )

        async def override_db():
            mock_session = AsyncMock()
            # 1. User auth lookup
            user_res = MagicMock()
            user_res.scalar_one_or_none.return_value = self.mock_user

            # 2. Reading lookup
            reading_res = MagicMock()
            reading_res.scalar_one_or_none.return_value = my_reading

            mock_session.execute.side_effect = [user_res, reading_res]
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()
            yield mock_session

        app.dependency_overrides[get_db_session] = override_db
        try:
            res = self.client.patch(
                f"/api/v1/readings/{my_reading.id}/favorite",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"is_favorite": True},
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res.json()["is_favorite"])
        finally:
            app.dependency_overrides.pop(get_db_session, None)
