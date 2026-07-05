from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import OrganizationStatus, SubscriptionPlan

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role
    from app.models.workspace import Workspace
    from app.models.dataset import Dataset
    from app.models.dashboard import Dashboard
    from app.models.ai_conversation import AIConversation
    from app.models.ai_recommendation import AIRecommendation
    from app.models.forecast_model import ForecastModel
    from app.models.report import Report
    from app.models.notification import Notification
    from app.models.audit_log import AuditLog
    from app.models.system_setting import SystemSetting


class Organization(BaseModel):
    """
    Represents a tenant organization in the Insights Forge platform.
    """

    __tablename__ = "organizations"

    __table_args__ = (
        Index("ix_organizations_industry", "industry"),
        Index("ix_organizations_status", "status"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(
            SubscriptionPlan,
            name="subscription_plan_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=SubscriptionPlan.FREE,
        server_default=SubscriptionPlan.FREE.value,
        nullable=False,
    )

    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(
            OrganizationStatus,
            name="organization_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=OrganizationStatus.ACTIVE,
        server_default=OrganizationStatus.ACTIVE.value,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    dashboards: Mapped[list["Dashboard"]] = relationship(
        "Dashboard",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        "AIConversation",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ai_recommendations: Mapped[list["AIRecommendation"]] = relationship(
        "AIRecommendation",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    forecast_models: Mapped[list["ForecastModel"]] = relationship(
        "ForecastModel",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    system_settings: Mapped[list["SystemSetting"]] = relationship(
        "SystemSetting",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
