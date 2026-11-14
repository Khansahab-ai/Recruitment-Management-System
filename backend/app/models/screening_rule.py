
from typing import Optional

from sqlmodel import SQLModel, Field


class ScreeningRule(SQLModel, table=True):

    rule_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    requisition_id: int = Field(
        foreign_key="jobrequisition.requisition_id",
        index=True
    )

    criteria_name: str

    weight: float = Field(
        gt=0,
        le=100
    )

    minimum_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    is_mandatory: bool = Field(default=False)
