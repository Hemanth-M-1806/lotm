import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.database import close_db_engine, get_engine
from app.core.exceptions import AppException
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Graceful startup and shutdown lifecycle management."""
    settings = get_settings()
    setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
    logger.info("Initializing LOTM Tarot API backend (%s environment)", settings.ENVIRONMENT)

    # Initialize connection pool
    try:
        get_engine()
        logger.info("Database connection engine initialized")
    except Exception as exc:
        logger.error("Failed to initialize database engine: %s", str(exc))

    yield

    logger.info("Shutting down LOTM Tarot API backend...")
    await close_db_engine()
    logger.info("Database connection engine disposed cleanly")


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Lord of the Mysteries Tarot API",
        description="Victorian Backlund occult tarot consultation and pathway lore API.",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID / Correlation Middleware
    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = req_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

    # Exception Handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None)
        errors = [
            {"field": ".".join(str(loc) for loc in err["loc"]), "issue": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "request_id": req_id,
                    "details": errors,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None)
        code_map = {
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            403: "FORBIDDEN",
            401: "UNAUTHORIZED",
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "request_id": req_id,
                    "details": [],
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = getattr(request.state, "request_id", None)
        logger.exception("Unhandled server exception [req_id=%s]: %s", req_id, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please contact support with the request ID.",
                    "request_id": req_id,
                    "details": [],
                }
            },
        )

    # Routes
    app.include_router(health_router)

    return app


app = create_application()
