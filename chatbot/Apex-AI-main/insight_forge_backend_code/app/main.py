"""DecisIQ backend — FastAPI entry point.

Mounts all v1 routers under /api/v1 and normalizes error responses to the
standard shape the frontend depends on:  {"error": {"code": ..., "message": ...}}
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import (
    auth,
    chat,
    datasets,
    decisions,
    ingestion,
    reports,
    sectors,
    simulate,
    thresholds,
    users,
)

app = FastAPI(title="DecisIQ API", version="1.0.0")

API_V1 = "/api/v1"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Wrap HTTPExceptions in the standard error envelope.

    Handlers may raise `detail` as either a plain string or a
    {"code", "message"} dict; both are normalized here.
    """
    if isinstance(exc.detail, dict):
        error = {"code": exc.detail.get("code", "error"), "message": exc.detail.get("message", "")}
    else:
        error = {"code": "error", "message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": error}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "invalid request", "details": exc.errors()}},
    )


@app.get(f"{API_V1}/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router, prefix=API_V1)
app.include_router(ingestion.router, prefix=API_V1)
app.include_router(datasets.router, prefix=API_V1)
app.include_router(sectors.router, prefix=API_V1)
app.include_router(decisions.router, prefix=API_V1)
app.include_router(chat.router, prefix=API_V1)
app.include_router(simulate.router, prefix=API_V1)
app.include_router(reports.router, prefix=API_V1)
app.include_router(thresholds.router, prefix=API_V1)
app.include_router(users.router, prefix=API_V1)
