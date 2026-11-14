
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.candidate import Candidate

class ResumeArtifact(SQLModel, table=True):

    resume_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    candidate_id: int = Field(
        foreign_key="candidate.candidate_id",
        index=True
    )

    file_name: str

    file_type: str = Field(default="PDF")

    file_path: Optional[str] = None

    upload_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    extraction_status: str = Field(default="PENDING")

    candidate: Optional["Candidate"] = Relationship(
        back_populates="resumes"
    )
