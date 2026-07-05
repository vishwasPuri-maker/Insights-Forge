from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import UploadStatus

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.user import User


class DatasetUpload(BaseModel):
    """
    Stores upload history for datasets.
    """

    __tablename__ = "dataset_uploads"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id"),
        nullable=False,
        index=True,
    )

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    upload_status: Mapped[UploadStatus] = mapped_column(
        Enum(
            UploadStatus,
            name="upload_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=UploadStatus.COMPLETED,
        server_default=UploadStatus.COMPLETED.value,
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="uploads",
        lazy="selectin",
    )

    uploader: Mapped["User"] = relationship(
        "User",
        back_populates="dataset_uploads",
        foreign_keys=[uploaded_by],
        lazy="selectin",
    )
