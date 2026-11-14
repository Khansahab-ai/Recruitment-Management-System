
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.skill import Skill

class CandidateSkill(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    candidate_id: int = Field(
        foreign_key="candidate.candidate_id",
        index=True
    )

    skill_id: int = Field(
        foreign_key="skill.skill_id",
        index=True
    )

    proficiency: str = Field(default="BEGINNER")

    candidate: Optional["Candidate"] = Relationship(
        back_populates="skills"
    )

    skill: Optional["Skill"] = Relationship(
        back_populates="candidates"
    )
