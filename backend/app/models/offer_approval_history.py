
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class OfferApprovalHistory(SQLModel, table=True):

    approval_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    offer_id: int = Field(
        foreign_key="offer.offer_id",
        index=True
    )

    approver_id: Optional[int] = None

    decision: str

    comments: Optional[str] = None

    approved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
