
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Interview(SQLModel, table=True):

    interview_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    interview_code: str = Field(
        unique=True,
        index=True
    )

    application_id: int = Field(
        foreign_key="application.application_id",
        index=True
    )

    round_name: str

    scheduled_start: datetime

    scheduled_end: datetime

    status: str = Field(default="SCHEDULED")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
