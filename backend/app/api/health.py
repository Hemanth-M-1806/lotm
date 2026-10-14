from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import literal, select
from app.core.database import get_engine
from app.core.logging import logger
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get("/health/live", response_model=HealthResponse)
async def liveness() -> HealthResponse:
    """Liveness probe: returns 200 if the process is responsive."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "Service not ready"}},
)
async def readiness() -> Response:
    """Readiness probe: validates connectivity to the PostgreSQL database."""
    now = datetime.now(timezone.utc)
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(select(literal(1)))

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "database": "healthy",
                "timestamp": now.isoformat(),
            },
        )
    except Exception as exc:
        logger.warning("Readiness probe database check failed: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": "unreachable",
                "timestamp": now.isoformat(),
            },
        )
