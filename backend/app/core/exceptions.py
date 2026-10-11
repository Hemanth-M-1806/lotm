from typing import Any, List, Optional


class AppException(Exception):
    """Base application exception with consistent code and status mapping."""

    def __init__(
        self,
        message: str,
        code: str = "BAD_REQUEST",
        status_code: int = 400,
        details: Optional[List[Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: Optional[List[Any]] = None) -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404, details=details)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: Optional[List[Any]] = None) -> None:
        super().__init__(message=message, code="CONFLICT", status_code=409, details=details)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required", details: Optional[List[Any]] = None) -> None:
        super().__init__(message=message, code="UNAUTHORIZED", status_code=401, details=details)


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied", details: Optional[List[Any]] = None) -> None:
        super().__init__(message=message, code="FORBIDDEN", status_code=403, details=details)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed", details: Optional[List[Any]] = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)
