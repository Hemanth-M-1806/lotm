import unittest
import uuid
from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base

class TestDomainModels(unittest.TestCase):
    def test_models_metadata_registered(self):
        from app.models.base import Base
        from app.models.pathway import Pathway, Sequence
        from app.models.card import TarotCard
        from app.models.user import User, UserPreferences
        from app.models.reading import Reading, ReadingCard

        tables = Base.metadata.tables
        expected_tables = {
            "pathways",
            "sequences",
            "tarot_cards",
            "users",
            "user_preferences",
            "readings",
            "reading_cards"
        }
        self.assertTrue(expected_tables.issubset(set(tables.keys())))

    def test_pathway_and_sequence_relationships(self):
        from app.models.pathway import Pathway, Sequence
        
        pathway = Pathway(
            id=1,
            name="Fool",
            chinese_name="愚者",
            description="Pathway of change, bizarre miracles, and spiritual manipulation."
        )
        sequence = Sequence(
            id=10,
            pathway_id=1,
            sequence_number=9,
            name="Seer",
            acting_method_summary="Interpretation and occult intuition."
        )
        self.assertEqual(pathway.name, "Fool")
        self.assertEqual(sequence.sequence_number, 9)

    def test_tarot_card_attributes(self):
        from app.models.card import TarotCard

        card = TarotCard(
            id=0,
            name="The Fool",
            arcana_type="major",
            card_number=0,
            pathway_id=1,
            upright_meaning="Beginnings, potential.",
            reversed_meaning="Recklessness.",
            mystical_lore="Lord of the Mysteries flavor."
        )
        self.assertEqual(card.id, 0)
        self.assertEqual(card.arcana_type, "major")
        self.assertEqual(card.card_number, 0)

    def test_user_and_reading_creation(self):
        from app.models.user import User
        from app.models.reading import Reading, ReadingCard

        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            username="klein",
            email="klein@moretti.org",
            display_name="Klein Moretti",
            password_hash="argon2id$hashedpassword"
        )
        reading = Reading(
            id=uuid.uuid4(),
            user_id=user.id,
            spread_type="three_card",
            question="Divination regarding the Antigonus family notebook."
        )
        reading_card = ReadingCard(
            id=uuid.uuid4(),
            reading_id=reading.id,
            card_id=0,
            position_index=0,
            position_name="Past",
            is_reversed=False
        )
        self.assertEqual(user.username, "klein")
        self.assertEqual(reading.spread_type, "three_card")
        self.assertEqual(reading_card.position_name, "Past")
