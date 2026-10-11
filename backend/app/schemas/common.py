from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    issue: str


class ErrorPayload(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: List[Any] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorPayload


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime
    version: str = "0.1.0"


class ReadinessResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
