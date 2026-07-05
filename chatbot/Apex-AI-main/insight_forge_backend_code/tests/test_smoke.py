"""Smoke tests for the auth + datasets vertical slice.

Runs against the configured DATABASE_URL. Creates the four in-scope tables
(organizations, users, user_sessions, datasets), exercises the full auth flow,
asserts the JWT carries organization_id + sector, checks the datasets endpoint,
then cleans up every row it created so the run is repeatable.
"""
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import (
    Dataset,
    DecisionCard,
    Organization,
    Record,
    User,
    UserSession,
)

API = "/api/v1"


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(engine)
    yield TestClient(app)


@pytest.fixture
def creds():
    return {
        "organization_name": "SmokeCo",
        "email": f"smoke-{uuid.uuid4().hex[:12]}@example.com",
        "password": "supersecret123",
        "sector": "retail",
    }


def _cleanup(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is not None:
            org_id = user.organization_id
            db.execute(delete(Record).where(Record.organization_id == org_id))
            db.execute(delete(DecisionCard).where(DecisionCard.organization_id == org_id))
            db.execute(delete(Dataset).where(Dataset.organization_id == org_id))
            db.execute(delete(UserSession).where(UserSession.user_id == user.id))
            db.execute(delete(User).where(User.id == user.id))
            db.execute(delete(Organization).where(Organization.id == org_id))
            db.commit()
    finally:
        db.close()


def test_health(client):
    r = client.get(f"{API}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_auth_and_datasets_flow(client, creds):
    try:
        # signup -> tokens
        r = client.post(f"{API}/auth/signup", json=creds)
        assert r.status_code == 201, r.text
        tokens = r.json()
        access = tokens["access_token"]

        # the access token must carry organization_id + sector
        payload = jwt.decode(access, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sector"] == "retail"
        assert "organization_id" in payload and payload["organization_id"]

        # login -> tokens
        r = client.post(
            f"{API}/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert r.status_code == 200, r.text

        # datasets list (empty, org-scoped) requires the bearer token
        r = client.get(f"{API}/datasets", headers={"Authorization": f"Bearer {access}"})
        assert r.status_code == 200, r.text
        assert r.json() == []

        # unauthenticated is rejected
        assert client.get(f"{API}/datasets").status_code == 401

        # refresh rotates the pair
        r = client.post(f"{API}/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert r.status_code == 200, r.text

        # signup with an invalid sector is a 422
        bad = {**creds, "email": f"bad-{uuid.uuid4().hex[:8]}@example.com", "sector": "banking"}
        assert client.post(f"{API}/auth/signup", json=bad).status_code == 422
    finally:
        _cleanup(creds["email"])


def _seed(email: str) -> None:
    """Insert a dataset, two records and a decision card for the org (retail)."""
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        org_id = user.organization_id
        ds = Dataset(
            organization_id=org_id,
            uploaded_by=user.id,
            sector="retail",
            original_filename="seed.csv",
            s3_key="seed/seed.csv",
            status="ready",
            health_score=92.5,
        )
        db.add(ds)
        db.flush()
        db.add_all(
            [
                Record(organization_id=org_id, dataset_id=ds.id, sector="retail",
                       data={"product": "A", "sales": 10}),
                Record(organization_id=org_id, dataset_id=ds.id, sector="retail",
                       data={"product": "B", "sales": 20}),
            ]
        )
        db.add(
            DecisionCard(
                organization_id=org_id, sector="retail",
                title="Restock product A", recommendation="Sales trending up",
                confidence_score=0.9, status="pending",
            )
        )
        db.commit()
    finally:
        db.close()


def test_sector_dashboards_decisions_and_chat(client, creds):
    try:
        access = client.post(f"{API}/auth/signup", json=creds).json()["access_token"]
        auth = {"Authorization": f"Bearer {access}"}
        _seed(creds["email"])

        # scorecard
        r = client.get(f"{API}/sectors/retail/scorecard", headers=auth)
        assert r.status_code == 200, r.text
        cards = {c["key"]: c["value"] for c in r.json()["cards"]}
        assert cards["records"] == 2
        assert cards["datasets_ready"] == 1
        assert cards["pending_decisions"] == 1

        # timeseries — frontend-ready {labels, series}
        r = client.get(f"{API}/sectors/retail/timeseries", headers=auth)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["series"][0]["name"] == "records"
        assert sum(body["series"][0]["values"]) == 2

        # records list + single
        r = client.get(f"{API}/sectors/retail/records", headers=auth)
        assert r.status_code == 200 and r.json()["total"] == 2
        rec_id = r.json()["items"][0]["id"]
        assert client.get(f"{API}/sectors/retail/records/{rec_id}", headers=auth).status_code == 200

        # wrong sector for this (retail) user -> 403
        assert client.get(f"{API}/sectors/service/scorecard", headers=auth).status_code == 403
        # unknown sector -> 404
        assert client.get(f"{API}/sectors/banking/scorecard", headers=auth).status_code == 404

        # decision cards: list, approve, then already-decided 409
        r = client.get(f"{API}/decision-cards", headers=auth)
        assert r.status_code == 200 and len(r.json()) == 1
        card_id = r.json()[0]["id"]
        r = client.post(f"{API}/decision-cards/{card_id}/approve", headers=auth)
        assert r.status_code == 200 and r.json()["status"] == "approved"
        assert client.post(f"{API}/decision-cards/{card_id}/reject", headers=auth).status_code == 409

        # chat websocket (stub reply since no LLM key)
        with client.websocket_connect(f"{API}/chat/stream?token={access}") as ws:
            ws.send_json({"message": "hello"})
            got_done = False
            for _ in range(50):
                frame = ws.receive_json()
                if frame["type"] == "done":
                    got_done = True
                    break
            assert got_done

        # chat rejects a bad token
        with pytest.raises(Exception):
            with client.websocket_connect(f"{API}/chat/stream?token=bad") as ws:
                ws.receive_json()
    finally:
        _cleanup(creds["email"])
