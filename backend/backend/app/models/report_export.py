from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import ExportFormat

if TYPE_CHECKING:
    from app.models.report import Report
    from app.models.user import User


class ReportExport(BaseModel):
    """
    Represents an exported report file.
    """

    __tablename__ = "report_exports"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id"),
        nullable=False,
        index=True,
    )

    exported_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    export_format: Mapped[ExportFormat] = mapped_column(
        Enum(
            ExportFormat,
            name="export_format_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    report: Mapped["Report"] = relationship(
        "Report",
        back_populates="exports",
        lazy="selectin",
    )

    exporter: Mapped["User"] = relationship(
        "User",
        back_populates="report_exports",
        foreign_keys=[exported_by],
        lazy="selectin",
    )
