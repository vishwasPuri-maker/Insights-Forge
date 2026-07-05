"""Standard error envelope: {"error": {"code", "message"}}.

Applied to raised HTTPExceptions (401/403/404/409/...). Request-body
validation (422) is intentionally left in FastAPI's default
``{"detail": [...]}`` shape because the frozen frontend contract
(HTTPValidationError) is integrated against it.
"""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """HTTPException carrying a stable machine-readable ``code``."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(status_code=status_code, detail=message)
        self.code = code


def _code_for_status(status_code: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_error",
    }.get(status_code, "error")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = getattr(exc, "code", None) or _code_for_status(exc.status_code)
    message = (
        exc.detail if isinstance(exc.detail, str) else _code_for_status(exc.status_code)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": message}},
        headers=getattr(exc, "headers", None),
    )
