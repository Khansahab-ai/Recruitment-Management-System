"""add database integrity constraints

Revision ID: e515d29ccbfa
Revises: 
Create Date: 2026-11-14 16:29:47.123493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e515d29ccbfa'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""

    op.create_unique_constraint(
        'uq_application_candidate_requisition',
        'application',
        ['candidate_id', 'requisition_id']
    )

    op.create_unique_constraint(
        'uq_feedback_interviewer',
        'feedback',
        ['interview_id', 'interviewer_id']
    )

    op.create_unique_constraint(
        'uq_interview_interviewer',
        'interviewassignment',
        ['interview_id', 'interviewer_id']
    )

    op.create_check_constraint(
        'ck_requisition_salary_range',
        'jobrequisition',
        'max_salary >= min_salary'
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'ck_requisition_salary_range',
        'jobrequisition',
        type_='check'
    )

    op.drop_constraint(
        'uq_interview_interviewer',
        'interviewassignment',
        type_='unique'
    )

    op.drop_constraint(
        'uq_feedback_interviewer',
        'feedback',
        type_='unique'
    )

    op.drop_constraint(
        'uq_application_candidate_requisition',
        'application',
        type_='unique'
    )
