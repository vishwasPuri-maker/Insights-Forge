from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import Sector, WorkspaceStatus
from app.models.audit import AuditMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace_member import WorkspaceMember
    from app.models.dataset import Dataset
    from app.models.dashboard import Dashboard
    from app.models.report import Report
    from app.models.ai_conversation import AIConversation


class Workspace(BaseModel, AuditMixin):
    """
    Represents an organization workspace.
    """

    __tablename__ = "workspaces"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    industry_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sector: Mapped[Sector] = mapped_column(
        Enum(
            Sector,
            name="sector_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=Sector.RETAIL,
        server_default=Sector.RETAIL.value,
        nullable=False,
        index=True,
    )

    status: Mapped[WorkspaceStatus] = mapped_column(
        Enum(
            WorkspaceStatus,
            name="workspace_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=WorkspaceStatus.ACTIVE,
        server_default=WorkspaceStatus.ACTIVE.value,
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="workspaces",
        lazy="selectin",
    )

    members: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    dashboards: Mapped[list["Dashboard"]] = relationship(
        "Dashboard",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        "AIConversation",
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
