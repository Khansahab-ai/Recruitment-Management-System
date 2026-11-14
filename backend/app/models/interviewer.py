
from typing import Optional

from sqlmodel import SQLModel, Field


class Interviewer(SQLModel, table=True):

    interviewer_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    interviewer_code: str = Field(
        unique=True,
        index=True
    )

    full_name: str

    email: str = Field(
        unique=True,
        index=True
    )

    department_id: int = Field(
        foreign_key="department.department_id"
    )

    is_active: bool = Field(default=True)
