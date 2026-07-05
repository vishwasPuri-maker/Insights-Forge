"""
app/models/vector_chunk.py
--------------------------
SQLAlchemy database model for storing embedded text chunks in PostgreSQL with pgvector.
This is Option A: isolated table for RAG scalability, chunking, and metadata.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.record import Record


class VectorChunk(BaseModel):
    """
    Represents a single embedded text chunk associated with an ingested Record.
    """

    __tablename__ = "vector_chunks"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("records.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # We use 384 dimensions for our default local sentence-transformers model.
    # PostgreSQL pgvector columns can still accept dynamic dimensions or check constraints in validation.
    embedding: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        lazy="raise",
    )

    record: Mapped["Record"] = relationship(
        "Record",
        lazy="raise",
    )
