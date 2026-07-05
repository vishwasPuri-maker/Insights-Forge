"""
Tests for Conversation Memory System
------------------------------------
Covers repository queries, context window compiling, token calculations,
memory metrics updates, and background task triggers.
"""

import uuid
import pytest
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient


# Register custom compiler to allow SQLite to render PostgreSQL JSONB columns as JSON
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


from app.db.database import Base  # noqa: E402
import app.db.base  # Register all models  # noqa: E402
from app.main import app  # noqa: E402
from app.api.deps import get_current_user, CurrentUser  # noqa: E402
from app.db.session import get_db  # noqa: E402

from app.models.organization import Organization  # noqa: E402
from app.models.workspace import Workspace  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.ai_conversation import AIConversation  # noqa: E402
from app.models.ai_message import AIMessage  # noqa: E402

from app.models.enums import (  # noqa: E402
    AIModel,
    AIMessageSender,
    SubscriptionPlan,
    OrganizationStatus,
    WorkspaceStatus,
    UserStatus,
    Sector,
)
from app.repositories.conversation_repository import (  # noqa: E402
    ConversationRepository,
)
from app.repositories.message_repository import MessageRepository  # noqa: E402
from app.core.memory.context_window import ContextWindowManager  # noqa: E402
from app.core.memory.conversation_memory_service import (  # noqa: E402
    ConversationMemoryService,
)
from app.core.memory.conversation_maintenance import (  # noqa: E402
    ConversationMaintenance,
)


# --- Mocking & Test Helpers ---


class MockBackgroundTasks(BackgroundTasks):
    """
    Mock class for verifying background task registrations.
    """

    def __init__(self):
        super().__init__()
        self.added_tasks = []

    def add_task(self, func, *args, **kwargs):
        self.added_tasks.append((func, args, kwargs))


# Create a consistent mock user context for endpoints testing
MOCK_USER_ID = uuid.uuid4()
MOCK_ORG_ID = uuid.uuid4()
MOCK_WORKSPACE_ID = uuid.uuid4()


# --- Database and Client Fixtures ---


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Creates a fresh, in-memory SQLite database and Session for isolated tests.
    Uses StaticPool to keep the database connection alive and prevent database wipes on commit.
    """
    # SQLite in-memory engine with StaticPool
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        # Pre-seed the mock tenant data required by relationship constraints
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
    """
    Creates a test client with overridden dependencies for API testing.
    """

    # Mock JWT decoder dependencies
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

    # Override endpoints database and authentication dependencies
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --- Unit Tests ---


def test_context_window_manager_token_estimation():
    """
    Verifies the context window manager estimates tokens and returns positive integers.
    """
    mgr = ContextWindowManager()
    text = "Hello world, this is a test text block."
    tokens = mgr.estimate_tokens(text)

    assert tokens > 0
    assert isinstance(tokens, int)

    messages = [
        {"role": "system", "content": "Instructions"},
        {"role": "user", "content": "Query"},
    ]
    total_tokens = mgr.estimate_messages_tokens(messages)
    assert total_tokens > 0
    assert isinstance(total_tokens, int)


def test_context_window_manager_order(db_session):
    """
    Verifies that the compiled prompt context is structured in the required priority order.
    """
    mgr = ContextWindowManager()

    convo = AIConversation(
        id=uuid.uuid4(),
        title="Test Conversation",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
        summary="Summarized history",
    )

    recent_messages = [
        AIMessage(
            conversation_id=convo.id,
            sender_type=AIMessageSender.USER,
            message="Initial User Query",
            tokens_used=4,
        ),
        AIMessage(
            conversation_id=convo.id,
            sender_type=AIMessageSender.AI,
            message="Initial AI Response",
            tokens_used=4,
        ),
    ]

    system_prompt = "System base instructions."
    messages = mgr.build_context(
        system_prompt=system_prompt, conversation=convo, recent_messages=recent_messages
    )

    # Priority context order checks:
    # 1. System Prompt
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt

    # 2. Conversation Summary
    assert messages[1]["role"] == "assistant"
    assert "Summarized history" in messages[1]["content"]

    # 3. Recent message history window (User -> Assistant)
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Initial User Query"
    assert messages[3]["role"] == "assistant"
    assert messages[3]["content"] == "Initial AI Response"


def test_repositories_crud(db_session):
    """
    Verifies ConversationRepository and MessageRepository perform basic CRUD operations.
    """
    convo_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    # 1. Create
    convo = convo_repo.create_conversation(
        title="First convo",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()
    assert convo.id is not None
    assert convo.total_messages == 0

    # 2. Retrieve
    found = convo_repo.get_conversation_by_id(convo.id, MOCK_WORKSPACE_ID, MOCK_ORG_ID)
    assert found is not None
    assert found.title == "First convo"

    # 3. Update
    convo_repo.update_conversation(convo, title="Updated title")
    db_session.commit()
    assert convo.title == "Updated title"

    # 4. Message Log
    msg_repo.create_message(
        conversation_id=convo.id,
        sender_type=AIMessageSender.USER,
        message="Hello world",
        tokens_used=3,
    )
    db_session.commit()

    messages = msg_repo.get_all_messages(convo.id)
    assert len(messages) == 1
    assert messages[0].message == "Hello world"


def test_tenant_isolation_in_repository(db_session):
    """
    Verifies that get_conversation_by_id checks organization_id and workspace_id boundaries.
    """
    convo_repo = ConversationRepository(db_session)

    convo = convo_repo.create_conversation(
        title="Isolated convo",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Correct tenant matches
    found = convo_repo.get_conversation_by_id(convo.id, MOCK_WORKSPACE_ID, MOCK_ORG_ID)
    assert found is not None

    # Mismatched organization_id boundary check -> should hide record
    assert (
        convo_repo.get_conversation_by_id(convo.id, MOCK_WORKSPACE_ID, uuid.uuid4())
        is None
    )

    # Mismatched workspace_id boundary check -> should hide record
    assert (
        convo_repo.get_conversation_by_id(convo.id, uuid.uuid4(), MOCK_ORG_ID) is None
    )


def test_soft_delete_exclusion(db_session):
    """
    Verifies soft-deleted conversation records are excluded from active list queries.
    """
    convo_repo = ConversationRepository(db_session)

    convo = convo_repo.create_conversation(
        title="Active thread",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Confirm visible initially
    active_convos = convo_repo.list_conversations(
        MOCK_WORKSPACE_ID, MOCK_ORG_ID, MOCK_USER_ID
    )
    assert len(active_convos) == 1

    # Apply soft deletion
    convo_repo.soft_delete_conversation(convo)
    db_session.commit()

    # Confirm excluded after soft delete
    active_convos_after = convo_repo.list_conversations(
        MOCK_WORKSPACE_ID, MOCK_ORG_ID, MOCK_USER_ID
    )
    assert len(active_convos_after) == 0


def test_conversation_metrics_and_aggregate_stats(db_session):
    """
    Verifies conversation metrics update correctly and aggregate statistics compute accurate totals.
    """
    convo_repo = ConversationRepository(db_session)

    # Create thread
    convo = convo_repo.create_conversation(
        title="Stats thread",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Log metrics updates
    now = datetime.now(timezone.utc)
    convo_repo.update_metrics(convo, message_tokens=150, message_time=now)
    convo_repo.update_conversation(convo, summary="Metrics generated summary")
    db_session.commit()

    assert convo.total_messages == 1
    assert convo.total_tokens == 150
    assert convo.last_message_at.replace(tzinfo=None) == now.replace(tzinfo=None)

    # Fetch aggregates
    stats = convo_repo.get_aggregate_stats(MOCK_WORKSPACE_ID, MOCK_ORG_ID)
    assert stats["conversation_count"] == 1
    assert stats["message_count"] == 1
    assert stats["average_tokens"] == 150.0
    assert stats["summaries_generated"] == 1


def test_conversation_memory_service(db_session):
    """
    Verifies ConversationMemoryService context compilation and exchange updates.
    """
    svc = ConversationMemoryService()

    # Create thread
    convo = svc.create_conversation(
        db=db_session,
        title="Service thread",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Save exchange logs
    svc.save_exchange(
        db=db_session,
        conversation_id=convo.id,
        user_message="Hello memory service",
        ai_message="I have persistent storage",
        user_tokens=5,
        ai_tokens=5,
        response_time_ms=120,
    )
    db_session.commit()

    assert convo.total_messages == 2
    assert convo.total_tokens == 10

    # Compile context
    ctx = svc.get_active_context(
        db=db_session,
        conversation_id=convo.id,
        system_prompt="Base instruction prompt.",
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
    )
    assert len(ctx) == 3  # 1 system + 2 turns (1 User, 1 AI)


# --- Background Triggers Tests ---


def test_background_title_generation_trigger(db_session):
    """
    Verifies that a title generation task is scheduled only when total messages == 2.
    """
    maint = ConversationMaintenance()
    bg_tasks = MockBackgroundTasks()

    convo_repo = ConversationRepository(db_session)

    convo = convo_repo.create_conversation(
        title="Title trigger convo",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )

    # Simulate first user turn + AI turn (total_messages = 2)
    convo.total_messages = 2
    db_session.commit()

    maint.run_maintenance(
        db=db_session,
        conversation_id=convo.id,
        background_tasks=bg_tasks,
        user_query="First user command",
        ai_response="First AI assessment",
    )

    # Verify background title generation task is added
    assert len(bg_tasks.added_tasks) == 1
    task_func, task_args, _ = bg_tasks.added_tasks[0]
    assert task_func.__name__ == "generate_title"
    assert task_args[0] == convo.id
    assert task_args[1] == "First user command"
    assert task_args[2] == "First AI assessment"


def test_background_summary_generation_trigger(db_session):
    """
    Verifies that summary consolidation task is scheduled when message thresholds are exceeded.
    """
    maint = ConversationMaintenance()
    bg_tasks = MockBackgroundTasks()

    convo_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    convo = convo_repo.create_conversation(
        title="Summary trigger convo",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Add messages exceeding settings.MEMORY_SUMMARY_THRESHOLD (which is 10)
    for i in range(12):
        msg_repo.create_message(
            conversation_id=convo.id,
            sender_type=AIMessageSender.USER if i % 2 == 0 else AIMessageSender.AI,
            message=f"Message index {i}",
            tokens_used=10,
        )
    db_session.commit()

    maint.run_maintenance(
        db=db_session,
        conversation_id=convo.id,
        background_tasks=bg_tasks,
        user_query="Current query",
        ai_response="Current response",
    )

    # Verify summarization task consolidated
    assert len(bg_tasks.added_tasks) == 1
    task_func, task_args, _ = bg_tasks.added_tasks[0]
    assert task_func.__name__ == "consolidate_summary"
    assert task_args[0] == convo.id
    assert task_args[1] is None  # old_summary
    assert len(task_args[2]) > 0  # list of message IDs passed


def test_no_summary_when_threshold_not_reached(db_session):
    """
    Verifies that no summary consolidation task is scheduled if message counts remain below thresholds.
    """
    maint = ConversationMaintenance()
    bg_tasks = MockBackgroundTasks()

    convo_repo = ConversationRepository(db_session)
    msg_repo = MessageRepository(db_session)

    convo = convo_repo.create_conversation(
        title="No summary convo",
        model_name=AIModel.LLAMA,
        workspace_id=MOCK_WORKSPACE_ID,
        organization_id=MOCK_ORG_ID,
        user_id=MOCK_USER_ID,
    )
    db_session.commit()

    # Add messages below summary threshold (e.g. only 4 messages)
    for i in range(4):
        msg_repo.create_message(
            conversation_id=convo.id,
            sender_type=AIMessageSender.USER if i % 2 == 0 else AIMessageSender.AI,
            message="Simple chat content turn",
            tokens_used=10,
        )
    db_session.commit()

    maint.run_maintenance(
        db=db_session,
        conversation_id=convo.id,
        background_tasks=bg_tasks,
        user_query="Current query",
        ai_response="Current response",
    )

    # Verify no summarization task is scheduled
    assert len(bg_tasks.added_tasks) == 0


# --- API Endpoint Integration Tests ---


def test_memory_health_endpoint(client):
    """
    Verifies that the /chat/memory/health API endpoint returns diagnostic stats correctly.
    """
    response = client.get("/api/v1/chat/memory/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["memory_enabled"] is True
    assert "conversation_count" in data
    assert "message_count" in data
    assert "average_messages" in data
    assert "average_tokens" in data
    assert "summaries_generated" in data
    assert "pending_background_jobs" in data
