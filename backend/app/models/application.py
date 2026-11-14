
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.requisition import JobRequisition


class Application(SQLModel, table=True):
    
    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "requisition_id",
            name="uq_application_candidate_requisition"
        ),
    )

    application_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    application_code: str = Field(
        unique=True,
        index=True
    )

    candidate_id: int = Field(
        foreign_key="candidate.candidate_id",
        index=True
    )

    requisition_id: int = Field(
        foreign_key="jobrequisition.requisition_id",
        index=True
    )

    status: str = Field(default="APPLIED")

    applied_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    screening_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    candidate: Optional["Candidate"] = Relationship()

    requisition: Optional["JobRequisition"] = Relationship()
