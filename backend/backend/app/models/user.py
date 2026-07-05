from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import UserStatus

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user_role import UserRole
    from app.models.user_session import UserSession
    from app.models.workspace_member import WorkspaceMember
    from app.models.dataset import Dataset
    from app.models.dataset_upload import DatasetUpload
    from app.models.analysis_job import AnalysisJob
    from app.models.ai_conversation import AIConversation
    from app.models.report_export import ReportExport
    from app.models.notification import Notification
    from app.models.audit_log import AuditLog
    from app.models.system_setting import SystemSetting


class User(BaseModel):
    """
    Represents a platform user.
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # User Information
    # ------------------------------------------------------------------

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False,
    )

    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            name="user_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value,
        nullable=False,
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile_image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="users",
        lazy="selectin",
    )

    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    workspace_members: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="uploader",
        foreign_keys="Dataset.uploaded_by",
        lazy="selectin",
    )

    dataset_uploads: Mapped[list["DatasetUpload"]] = relationship(
        "DatasetUpload",
        back_populates="uploader",
        foreign_keys="DatasetUpload.uploaded_by",
        lazy="selectin",
    )

    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        back_populates="initiated_user",
        foreign_keys="AnalysisJob.initiated_by",
        lazy="selectin",
    )

    created_analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        foreign_keys="AnalysisJob.created_by",
        lazy="selectin",
        viewonly=True,
    )

    updated_analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        foreign_keys="AnalysisJob.updated_by",
        lazy="selectin",
        viewonly=True,
    )

    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        "AIConversation",
        back_populates="user",
        foreign_keys="AIConversation.user_id",
        lazy="selectin",
    )

    report_exports: Mapped[list["ReportExport"]] = relationship(
        "ReportExport",
        back_populates="exporter",
        foreign_keys="ReportExport.exported_by",
        lazy="selectin",
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        foreign_keys="AuditLog.user_id",
        lazy="selectin",
    )

    system_settings: Mapped[list["SystemSetting"]] = relationship(
        "SystemSetting",
        back_populates="updater",
        foreign_keys="SystemSetting.updated_by",
        lazy="selectin",
    )
