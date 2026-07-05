"""
Tests for Production LLM Integration
------------------------------------
Covers streaming, retry logic, timeout metrics, health diagnostics,
prompt builder ordering, and client disconnect cancellation safety.
"""

import pytest
import uuid
import httpx
from unittest.mock import Mock, MagicMock, patch
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base
import app.db.base
from app.main import app
from app.api.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.core.config import settings

from app.models.organization import Organization
from app.models.workspace import Workspace
from app.models.user import User
from app.models.ai_conversation import AIConversation
from app.models.enums import (
    AIModel,
    AIMessageSender,
    SubscriptionPlan,
    OrganizationStatus,
    WorkspaceStatus,
    UserStatus,
    Sector,
)

from app.core.llm.token_counter import TokenCounter
from app.core.llm.prompt_builder import StructuredPromptBuilder
from app.core.llm.factory import LLMFactory
from app.core.llm.providers.ollama import OllamaProvider
from app.core.llm.provider import LLMChunk, LLMHealthCheckResponse

# Custom SQL compiler for JSONB columns on SQLite
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


MOCK_USER_ID = uuid.uuid4()
MOCK_ORG_ID = uuid.uuid4()
MOCK_WORKSPACE_ID = uuid.uuid4()


from sqlalchemy.pool import StaticPool  # noqa: E402


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        org = Organization(
            id=MOCK_ORG_ID,
            name="Test Org",
            slug="test-org",
            industry="Retail",
            subscription_plan=SubscriptionPlan.FREE,
            status=OrganizationStatus.ACTIVE,
        )
        ws = Workspace(
            id=MOCK_WORKSPACE_ID,
            organization_id=MOCK_ORG_ID,
            name="Test WS",
            industry_type="Retail",
            sector=Sector.RETAIL,
            status=WorkspaceStatus.ACTIVE,
        )
        user = User(
            id=MOCK_USER_ID,
            organization_id=MOCK_ORG_ID,
            first_name="Test",
            last_name="User",
            email="test@test.com",
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
def client(db_session) -> Generator[TestClient, None, None]:
    class MockUser:
        id = MOCK_USER_ID
        organization_id = MOCK_ORG_ID
        workspace_id = MOCK_WORKSPACE_ID
        status = "Active"
        is_deleted = False

    def override_get_current_user():
        return CurrentUser(
            user=MockUser(),
            organization_id=MOCK_ORG_ID,
            role="admin",
            workspace_id=MOCK_WORKSPACE_ID,
            sector="retail",
        )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_token_counter():
    assert TokenCounter.estimate_tokens("Hello world") == 2
    assert TokenCounter.estimate_tokens("") == 0


def test_prompt_builder():
    system = "System rule"
    summary = "Old summaries"
    from app.models.ai_message import AIMessage

    recent = [
        AIMessage(
            conversation_id=uuid.uuid4(),
            sender_type=AIMessageSender.USER,
            message="Initial",
            tokens_used=1,
        )
    ]
    rag = "Retrieved records"
    query = "User prompt"

    messages = StructuredPromptBuilder.build_messages(
        system_prompt=system,
        summary=summary,
        recent_messages=recent,
        rag_context=rag,
        query=query,
    )

    # Check ordering
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert "Retrieved records" in messages[0]["content"]
    assert messages[1]["role"] == "assistant"
    assert "Old summaries" in messages[1]["content"]
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Initial"
    assert messages[3]["role"] == "user"
    assert messages[3]["content"] == "User prompt"


def test_provider_factory():
    provider = LLMFactory.get_provider()
    # Provider-agnostic: just verify it satisfies the LLMProvider contract
    from app.core.llm.provider import LLMProvider as LLMProviderBase
    assert isinstance(provider, LLMProviderBase)

    # Temporarily set unsupported
    orig = settings.LLM_PROVIDER
    settings.LLM_PROVIDER = "unsupported_provider"
    try:
        with pytest.raises(ValueError) as exc:
            LLMFactory.get_provider()
        assert "Unsupported LLM provider" in str(exc.value)
    finally:
        settings.LLM_PROVIDER = orig


@patch("httpx.Client.post")
def test_retry_executor_success(mock_post):
    # Setup mock to fail twice, then succeed
    mock_post.side_effect = [
        httpx.TimeoutException("Timeout"),
        httpx.RequestError("Network error"),
        Mock(status_code=200, json=lambda: {"message": {"content": "Success content"}}),
    ]

    provider = OllamaProvider()
    res = provider.generate([{"role": "user", "content": "Hi"}])

    assert res.status == "success"
    assert res.content == "Success content"
    assert res.retry_count == 2


@patch("httpx.Client.post")
def test_retry_executor_exhausted(mock_post):
    # Setup mock to always fail
    mock_post.side_effect = httpx.TimeoutException("Timeout")

    provider = OllamaProvider()
    res = provider.generate([{"role": "user", "content": "Hi"}])

    assert res.status == "error"
    assert "inference engine is currently unavailable" in res.content


@patch("httpx.Client.send")
def test_stream_chunks_generation(mock_send):
    # Mock Response object yielding lines
    mock_resp = MagicMock(status_code=200)
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    mock_resp.iter_lines.return_value = [
        b'{"message": {"content": "Hello"}, "done": false}',
        b'{"message": {"content": " world"}, "done": true}',
    ]
    mock_send.return_value = mock_resp

    provider = OllamaProvider()
    chunks = list(provider.stream([{"role": "user", "content": "Hi"}]))

    assert len(chunks) == 2
    assert chunks[0].text == "Hello"
    assert chunks[0].finished is False
    assert chunks[1].text == " world"
    assert chunks[1].finished is True


@patch("httpx.Client.send")
def test_stream_interruption_handling(mock_send):
    # Mock response throwing mid-stream
    mock_resp = MagicMock(status_code=200)
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    def iter_lines_generator():
        yield b'{"message": {"content": "Partial"}, "done": false}'
        raise httpx.ReadTimeout("Read Timeout")

    mock_resp.iter_lines.side_effect = iter_lines_generator
    mock_send.return_value = mock_resp

    provider = OllamaProvider()
    chunks = list(provider.stream([{"role": "user", "content": "Hi"}]))

    assert len(chunks) == 2
    assert chunks[0].text == "Partial"
    assert chunks[0].finished is False
    assert "[Inference stream interrupted]" in chunks[1].text
    assert chunks[1].finished is True
    assert chunks[1].finish_reason == "error"


@patch("app.services.chat_service.SessionLocal")
@patch("app.services.chat_service.MultiAgentRouter")
def test_client_disconnect_cancellation_safety(
    mock_router_class, mock_session_local, db_session
):
    # Tests that when GeneratorExit is raised in get_chat_completion_stream,
    # the partial stream text is still safely persisted in the database.
    convo = AIConversation(
        id=uuid.uuid4(),
        title="Streaming test thread",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.add(convo)
    db_session.commit()
    convo_id = convo.id

    # Prevent the finally block from closing our test session
    db_session.close = MagicMock()
    mock_session_local.return_value = db_session

    # Mock the router instance returned
    mock_router = mock_router_class.return_value
    mock_router.route_query.return_value = {
        "role": "TrendAnalysisAgent",
        "analysis_type": "trend_analysis",
        "context": "Mocked RAG context",
        "confidence": "HIGH",
    }

    class MockStreamProvider:
        model = "gemma:2b"

        def stream(self, messages, **kwargs):
            yield LLMChunk(text="First chunk", finished=False, retry_count=0)
            yield LLMChunk(text=" Second chunk", finished=False, retry_count=0)
            # Simulate GeneratorExit raise inside client loop
            raise GeneratorExit()

    from app.services.chat_service import ChatService

    chat_svc = ChatService()
    chat_svc.llm_provider = MockStreamProvider()

    mock_curr_user = CurrentUser(
        user=db_session.get(User, MOCK_USER_ID),
        organization_id=MOCK_ORG_ID,
        role="admin",
        workspace_id=MOCK_WORKSPACE_ID,
        sector="retail",
    )

    stream_gen = chat_svc.get_chat_completion_stream(
        db=db_session,
        query="Client query",
        response_mode="MODE_BUSINESS",
        current_user=mock_curr_user,
        conversation_id=convo_id,
    )

    try:
        next(stream_gen)
        stream_gen.close()
    except Exception:
        pass

    from app.repositories.message_repository import MessageRepository

    msg_repo = MessageRepository(db_session)
    messages = msg_repo.get_all_messages(convo_id)

    assert len(messages) >= 1
    assert messages[0].message == "Client query"
    assert messages[0].sender_type == AIMessageSender.USER

    db_session.expire_all()
    all_convo_messages = msg_repo.get_all_messages(convo_id)
    ai_messages = [m for m in all_convo_messages if m.sender_type == AIMessageSender.AI]

    assert len(ai_messages) == 1
    assert ai_messages[0].message == "First chunk"


@patch("app.services.chat_service.ChatService.get_llm_health")
def test_diagnostics_health_endpoint(mock_health, client):
    mock_health.return_value = {
        "reachable": True,
        "model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else settings.LLM_MODEL,
        "version": "test-version",
        "latency_ms": 10,
    }

    response = client.get("/api/v1/chat/memory/health")
    assert response.status_code == 200

    response_health = client.get("/api/v1/chat/health")
    assert response_health.status_code == 200
    data = response_health.json()
    assert data["reachable"] is True
    assert data["version"] == "test-version"
