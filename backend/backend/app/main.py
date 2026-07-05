import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import app.db.base  # noqa: F401  -- registers all ORM models/mappers
from app.core.celery_app import celery_app  # noqa: F401
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import http_exception_handler

# Path to the Vite production build (frontend/dist/)
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


# ── Serve React SPA ──────────────────────────────────────────────────────────
# Mount static assets (JS/CSS chunks) at /assets
if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """
        Catch-all: return the React index.html for any non-API route so that
        React Router handles client-side navigation.
        """
        # Serve existing static files (favicon, manifest, etc.) directly
        static_file = FRONTEND_DIST / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        # Fall back to SPA shell for all other paths
        return FileResponse(str(FRONTEND_DIST / "index.html"))

