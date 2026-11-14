
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.candidate_skill import CandidateSkill

class Skill(SQLModel, table=True):

    skill_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    skill_name: str = Field(
        unique=True,
        index=True
    )

    category: Optional[str] = None

    candidates: list["CandidateSkill"] = Relationship(
        back_populates="skill"
    )
