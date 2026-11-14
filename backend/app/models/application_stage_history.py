
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class ApplicationStageHistory(SQLModel, table=True):

    event_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    application_id: int = Field(
        foreign_key="application.application_id",
        index=True
    )

    previous_status: Optional[str] = None

    new_status: str

    changed_by: Optional[str] = None

    reason: Optional[str] = None

    changed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
