
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class Offer(SQLModel, table=True):

    offer_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    offer_code: str = Field(
        unique=True,
        index=True
    )

    application_id: int = Field(
        foreign_key="application.application_id",
        index=True
    )

    offered_salary: float = Field(gt=0)

    joining_date: Optional[datetime] = None

    status: str = Field(default="PENDING_APPROVAL")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
