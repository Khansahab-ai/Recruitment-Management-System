
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.department import Department


class JobRequisition(SQLModel, table=True):

    __table_args__ = (
        CheckConstraint(
            "max_salary >= min_salary",
            name="ck_requisition_salary_range"
        ),
    )

    requisition_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    job_code: str = Field(unique=True, index=True)
    job_title: str

    department_id: int = Field(
        foreign_key="department.department_id"
    )

    openings: int = Field(gt=0)
    min_salary: float = Field(gt=0)
    max_salary: float = Field(gt=0)
    experience_required: float = Field(default=0, ge=0)
    status: str = Field(default="DRAFT")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    department: Optional["Department"] = Relationship(
        back_populates="requisitions"
    )
