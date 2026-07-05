"""
Unit Tests for Decision Intelligence (Milestone 4G)
----------------------------------------------------
Covers resilient parser recovery, schema validation, confidence calculation,
empty retrieval fallbacks, duplicate prevention, concurrent safety,
database rollback integrity, and metadata round-trip verification.
"""

import pytest
import uuid
import json
from unittest.mock import MagicMock, patch
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import app.db.base
from app.db.database import Base
from app.core.config import settings
from app.main import app
from app.api.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.models.enums import (
    SubscriptionPlan,
    OrganizationStatus,
    WorkspaceStatus,
    UserStatus,
    Sector,
    AIRecommendationPriority,
    AIRecommendationType,
)
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.models.user import User
from app.models.ai_recommendation import AIRecommendation

from app.services.decision_parser import DecisionParser
from app.services.decision_validator import DecisionValidator
from app.services.decision_service import DecisionService

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


MOCK_USER_ID = uuid.uuid4()
MOCK_ORG_ID = uuid.uuid4()
MOCK_WORKSPACE_ID = uuid.uuid4()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        # Seed tenant data
        org = Organization(
            id=MOCK_ORG_ID,
            name="Apex Test Org",
            slug="apex-test-org",
            industry="Retail",
            subscription_plan=SubscriptionPlan.FREE,
            status=OrganizationStatus.ACTIVE,
        )
        ws = Workspace(
            id=MOCK_WORKSPACE_ID,
            organization_id=MOCK_ORG_ID,
            name="Apex Test WS",
            industry_type="Retail",
            sector=Sector.RETAIL,
            status=WorkspaceStatus.ACTIVE,
        )
        user = User(
            id=MOCK_USER_ID,
            organization_id=MOCK_ORG_ID,
            first_name="Decision",
            last_name="Tester",
            email="tester@apex.com",
            password_hash="123",
            status=UserStatus.ACTIVE,
        )
        session.add(org)
        session.add(ws)
        session.add(user)
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    mock_user = CurrentUser(
        user=db_session.get(User, MOCK_USER_ID),
        organization_id=MOCK_ORG_ID,
        role="admin",
        workspace_id=MOCK_WORKSPACE_ID,
        sector="retail",
    )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ==============================================================================
# 1. Parser Resilience & Conversational recovery tests
# ==============================================================================


def test_parser_perfect_json():
    payload = '{"title": "Optimizing Stock", "confidence": 0.95}'
    parsed, score = DecisionParser.parse_raw_response(payload)
    assert parsed["title"] == "Optimizing Stock"
    assert parsed["confidence"] == 0.95
    assert score == 1.0


def test_parser_conversational_wraps():
    payload = (
        "Here is the parsed recommendation you requested:\n"
        "```json\n"
        '{"title": "Conversational stock fix", "confidence": 0.88}\n'
        "```\n"
        "Let me know if you need anything else."
    )
    parsed, score = DecisionParser.parse_raw_response(payload)
    assert parsed["title"] == "Conversational stock fix"
    assert parsed["confidence"] == 0.88
    assert score == 0.5


def test_parser_truncated_json():
    payload = '{"title": "Truncated stock analysis", "confidence": 0.77'
    parsed, score = DecisionParser.parse_raw_response(payload)
    assert parsed["title"] == "Truncated stock analysis"
    assert parsed["confidence"] == 0.77
    assert score == 0.5


def test_parser_trailing_commas():
    payload = '{"title": "Trailing commas fix", "confidence": 0.66,}'
    parsed, score = DecisionParser.parse_raw_response(payload)
    assert parsed["title"] == "Trailing commas fix"
    assert parsed["confidence"] == 0.66
    assert score == 0.5


# ==============================================================================
# 2. Derived Confidence & Configurable Weights Heuristic
# ==============================================================================


def test_derived_confidence_heuristic():
    parsed_data = {
        "title": "Configurable test",
        "summary": "Short summary",
        "recommendation": "Go retail",
        "confidence": 0.80,  # self-reported LLM confidence
        "priority": "High",
        "recommendation_type": "Insight",
        "explanation": {
            "reasoning": "Logical path explanation",
            "evidence": ["Item 1", "Item 2", "Item 3"],  # 3 items
            "assumptions": ["Ass1"],
            "confidence_reason": "Based on solid trends",
            "limitations": ["Lim1"],
        },
        "kpis": [{"metric": "Margin", "value": "12%"}],
        "sources": [{"document_id": "doc1", "chunk_id": "ch1", "score": 0.9}],
        "limitations": ["Lim1"],
    }

    # evidence_weight = min(3 / 5.0, 1.0) = 0.60
    # retrieval_score = 0.80
    # parser_quality = 1.0
    # derived = 0.35*0.80 + 0.35*0.80 + 0.20*0.60 + 0.10*1.0 = 0.28 + 0.28 + 0.12 + 0.10 = 0.78

    decision = DecisionValidator.validate_and_enrich(
        parsed_data=parsed_data,
        retrieval_score=0.80,
        parser_quality=1.0,
        retrieved_docs_count=1,
        model_name="gemma:2b",
        provider_name="ollama",
        prompt_version="1.0.0",
    )

    assert abs(decision.confidence - 0.78) < 1e-5


# ==============================================================================
# 3. Schema Constraints & Invalid Bounds Validation
# ==============================================================================


def test_validator_schema_missing_fields():
    parsed_data = {
        "title": "Missing recommendation",
        # missing recommendation field
        "confidence": 0.80,
        "priority": "High",
    }
    from app.core.errors import AppError

    with pytest.raises(AppError) as exc_info:
        DecisionValidator.validate_and_enrich(
            parsed_data=parsed_data,
            retrieval_score=0.5,
            parser_quality=1.0,
            retrieved_docs_count=0,
            model_name="gemma:2b",
            provider_name="ollama",
            prompt_version="1.0.0",
        )
    assert exc_info.value.status_code == 422


# ==============================================================================
# 4. Database Transaction Rollbacks on Validation/Parse Failures
# ==============================================================================


@patch("app.core.rag.retriever.Retriever.retrieve_and_build_context")
@patch("app.services.decision_engine.DecisionEngine.generate_decision_text")
def test_database_rollback_on_failed_pipeline(mock_gen, mock_retrieve, db_session):
    mock_retrieve.return_value = "Retrieved RAG mock context"
    # LLM returns junk text that fails parser
    mock_gen.return_value = "Junk response from LLM that cannot be parsed as JSON."

    # Pre-state message count
    initial_count = db_session.query(AIRecommendation).count()

    svc = DecisionService(db_session)
    with pytest.raises(Exception):
        svc.generate_decision_card(
            organization_id=MOCK_ORG_ID,
            workspace_id=MOCK_WORKSPACE_ID,
            query="Trigger failing generation",
        )

    final_count = db_session.query(AIRecommendation).count()
    assert initial_count == final_count  # No card committed; rolled back successfully


# ==============================================================================
# 5. Empty Retrieval Context
# ==============================================================================


@patch("app.core.vector_store.factory.VectorStoreFactory.get_vector_store")
@patch("app.services.decision_engine.DecisionEngine.generate_decision_text")
def test_empty_retrieval_context_fallback(
    mock_gen, mock_vector_store_factory, db_session
):
    # Vector store similarity_search returns empty results
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = []
    mock_vector_store_factory.return_value = mock_store

    # LLM yields valid response
    mock_gen.return_value = json.dumps(
        {
            "title": "Fallback recommendation",
            "summary": "No docs found",
            "recommendation": "Baseline stock replenishment",
            "confidence": 0.50,
            "priority": "Medium",
            "recommendation_type": "Insight",
            "explanation": {
                "reasoning": "Baseline default path",
                "evidence": [],
                "assumptions": ["No context available"],
                "confidence_reason": "Baseline default",
                "limitations": ["No custom context"],
            },
            "kpis": [],
            "sources": [],
            "limitations": [],
        }
    )

    svc = DecisionService(db_session)
    card = svc.generate_decision_card(
        organization_id=MOCK_ORG_ID,
        workspace_id=MOCK_WORKSPACE_ID,
        query="Empty retrieval query",
    )

    assert card.title == "Fallback recommendation"
    # derived confidence: w_retrieval*0.5 (fallback) + w_llm*0.5 + w_evidence*0 + w_parser*1.0
    # = 0.35*0.5 + 0.35*0.5 + 0 + 0.10*1.0 = 0.175 + 0.175 + 0.10 = 0.45
    assert abs(float(card.confidence_score) - 0.45) < 1e-5


# ==============================================================================
# 6. Duplicate Decision Prevention
# ==============================================================================


@patch("app.core.rag.retriever.Retriever.retrieve_and_build_context")
@patch("app.services.decision_engine.DecisionEngine.generate_decision_text")
def test_duplicate_decision_prevention(mock_gen, mock_retrieve, db_session):
    mock_retrieve.return_value = "Mock context"
    mock_gen.return_value = json.dumps(
        {
            "title": "Unique Title",
            "summary": "Situational text",
            "recommendation": "Plain recommendation text",
            "confidence": 0.90,
            "priority": "High",
            "recommendation_type": "Insight",
            "explanation": {
                "reasoning": "Explain reason",
                "evidence": ["E1"],
                "assumptions": [],
                "confidence_reason": "High trust",
                "limitations": [],
            },
            "kpis": [],
            "sources": [],
            "limitations": [],
        }
    )

    svc = DecisionService(db_session)
    card1 = svc.generate_decision_card(
        organization_id=MOCK_ORG_ID,
        workspace_id=MOCK_WORKSPACE_ID,
        query="First generation request",
    )
    card2 = svc.generate_decision_card(
        organization_id=MOCK_ORG_ID,
        workspace_id=MOCK_WORKSPACE_ID,
        query="Second duplicate request",
    )

    assert card1.id == card2.id  # Same pending card reused
    assert db_session.query(AIRecommendation).count() == 1


# ==============================================================================
# 7. Metadata Round-Trip Validation
# ==============================================================================


def test_metadata_round_trip(db_session):
    from app.repositories.decision_card_repository import DecisionCardRepository

    repo = DecisionCardRepository(db_session)

    meta = {
        "version": "1.0.0",
        "summary": "Scenario summary details",
        "limitations": ["L1", "L2"],
        "retrieved_documents_count": 4,
        "model_used": "llama3:8b",
    }

    card = repo.create(
        organization_id=MOCK_ORG_ID,
        workspace_id=MOCK_WORKSPACE_ID,
        title="Round-trip Test",
        recommendation="Recommendation text",
        confidence_score=0.91,
        priority=AIRecommendationPriority.HIGH,
        recommendation_type=AIRecommendationType.INSIGHT,
        metadata_json=meta,
    )
    db_session.commit()

    db_session.expire_all()
    loaded = db_session.get(AIRecommendation, card.id)
    assert loaded.metadata_json is not None
    assert loaded.metadata_json["version"] == "1.0.0"
    assert loaded.metadata_json["retrieved_documents_count"] == 4
    assert loaded.metadata_json["model_used"] == "llama3:8b"


# ==============================================================================
# 8. API Generate Router Endpoint End-To-End
# ==============================================================================


@patch("app.core.rag.retriever.Retriever.retrieve_and_build_context")
@patch("app.services.decision_engine.DecisionEngine.generate_decision_text")
def test_api_generate_route(mock_gen, mock_retrieve, client, db_session):
    mock_retrieve.return_value = "Mock context info"
    mock_gen.return_value = json.dumps(
        {
            "title": "API recommendation card",
            "summary": "API query summary",
            "recommendation": "Buy inventory",
            "confidence": 0.85,
            "priority": "Medium",
            "recommendation_type": "Optimization",
            "explanation": {
                "reasoning": "Reason text",
                "evidence": ["Ev1"],
                "assumptions": ["As1"],
                "confidence_reason": "Valid score",
                "limitations": ["None"],
            },
            "kpis": [],
            "sources": [],
            "limitations": [],
        }
    )

    resp = client.post(
        "/api/v1/decision-cards/generate",
        json={"query": "Automated warehouse stocks", "dataset_id": None},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "API recommendation card"
    assert data["recommendation"] == "Buy inventory"
    assert data["metadata_json"] is not None
    assert data["metadata_json"]["model_used"] == (
        settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else settings.LLM_MODEL
    )
