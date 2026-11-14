
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.candidate_skill import CandidateSkill
    from app.models.resume import ResumeArtifact

class Candidate(SQLModel, table=True):

    candidate_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    candidate_code: str = Field(
        unique=True,
        index=True
    )

    full_name: str

    email: str = Field(
        unique=True,
        index=True
    )

    phone: Optional[str] = None

    education: Optional[str] = None

    total_experience: float = Field(default=0, ge=0)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    skills: list["CandidateSkill"] = Relationship(
        back_populates="candidate"
    )

    resumes: list["ResumeArtifact"] = Relationship(
        back_populates="candidate"
    )
