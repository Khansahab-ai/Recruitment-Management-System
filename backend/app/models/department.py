
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.requisition import JobRequisition


class Department(SQLModel, table=True):

    department_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        index=True,
        unique=True,
        max_length=100
    )

    description: Optional[str] = None

    requisitions: list["JobRequisition"] = Relationship(
        back_populates="department"
    )
