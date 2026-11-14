
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint

class InterviewAssignment(SQLModel, table=True):

    __table_args__ = (
        UniqueConstraint(
            "interview_id",
            "interviewer_id",
            name="uq_interview_interviewer"
        ),
    )

    assignment_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    interview_id: int = Field(
        foreign_key="interview.interview_id",
        index=True
    )

    interviewer_id: int = Field(
        foreign_key="interviewer.interviewer_id",
        index=True
    )
