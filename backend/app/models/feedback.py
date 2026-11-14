
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class Feedback(SQLModel, table=True):

    __table_args__ = (
        UniqueConstraint(
            "interview_id",
            "interviewer_id",
            name="uq_feedback_interviewer"
        ),
    )

    feedback_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    feedback_code: str = Field(
        unique=True,
        index=True
    )

    interview_id: int = Field(
        foreign_key="interview.interview_id",
        index=True
    )

    interviewer_id: int = Field(
        foreign_key="interviewer.interviewer_id",
        index=True
    )

    technical_score: float = Field(ge=0, le=10)

    problem_solving_score: float = Field(ge=0, le=10)

    communication_score: float = Field(ge=0, le=10)

    overall_score: float = Field(ge=0, le=10)

    recommendation: str

    comments: Optional[str] = None

    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
