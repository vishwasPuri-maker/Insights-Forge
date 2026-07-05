"""
Chat Schemas
------------
Pydantic validation models for the AI memory systems, conversation lifecycles, and health metrics.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import AIConversationStatus, AIModel, AIMessageSender


class AIMessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_type: AIMessageSender
    message: str
    tokens_used: int
    response_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    model_name: AIModel = AIModel.LLAMA


class AIConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    model_name: Optional[AIModel] = None
    status: Optional[AIConversationStatus] = None


class AIConversationOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    model_name: AIModel
    status: AIConversationStatus
    summary: Optional[str] = None
    total_messages: int
    total_tokens: int
    last_message_at: Optional[datetime] = None
    last_summary_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIConversationDetailOut(AIConversationOut):
    messages: List[AIMessageOut] = Field(default_factory=list)


class MemoryHealthOut(BaseModel):
    status: str
    memory_enabled: bool
    conversation_count: int
    message_count: int
    average_messages: float
    average_tokens: float
    summaries_generated: int
    pending_background_jobs: int


class VectorHealthOut(BaseModel):
    provider: str
    embedding_provider: str
    model: str
    dimension: int
    status: str
    indexed_documents: int
    extension_installed: bool
    latency: float
    diagnostics: dict
