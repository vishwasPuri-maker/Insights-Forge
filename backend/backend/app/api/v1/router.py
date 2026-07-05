"""Aggregate /api/v1 router. Feature routers are mounted here as phases land."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    chat,
    datasets,
    decision_cards,
    ingestion,
    reports,
    sectors,
    simulate,
    thresholds,
    users,
)

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(ingestion.router)
api_router.include_router(datasets.router)
api_router.include_router(sectors.router)
api_router.include_router(decision_cards.router)
api_router.include_router(simulate.router)
api_router.include_router(reports.router)
api_router.include_router(thresholds.router)
api_router.include_router(users.router)
