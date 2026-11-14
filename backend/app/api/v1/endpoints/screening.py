from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.screening_rule import ScreeningRule
from app.models.requisition import JobRequisition
from app.models.application import Application
from app.schemas.recruitment import (
    ScreeningRuleCreate,
    ScreeningRuleRead,
    ScreeningEvaluationResult
)
from app.services.screening_service import evaluate_application

router = APIRouter()


@router.get("/rules", response_model=list[ScreeningRuleRead])
def get_screening_rules(
    requisition_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session)
):
    query = select(ScreeningRule)
    if requisition_id:
        query = query.where(ScreeningRule.requisition_id == requisition_id)
    return session.exec(query).all()


@router.post("/rules", response_model=ScreeningRuleRead, status_code=201)
def create_screening_rule(
    rule_data: ScreeningRuleCreate,
    session: Session = Depends(get_session)
):
    requisition = session.get(JobRequisition, rule_data.requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Job requisition not found")

    # Validate that total weights for this requisition do not exceed 100
    existing_rules = session.exec(
        select(ScreeningRule).where(ScreeningRule.requisition_id == rule_data.requisition_id)
    ).all()
    current_weight_sum = sum(r.weight for r in existing_rules)
    if current_weight_sum + rule_data.weight > 100.0:
        raise HTTPException(
            status_code=422,
            detail=f"Screening rules weight total cannot exceed 100% (currently {current_weight_sum}% + {rule_data.weight}%)"
        )

    rule = ScreeningRule(
        requisition_id=rule_data.requisition_id,
        criteria_name=rule_data.criteria_name,
        weight=rule_data.weight,
        minimum_score=rule_data.minimum_score,
        is_mandatory=rule_data.is_mandatory
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


@router.post("/evaluate/{application_id}", response_model=ScreeningEvaluationResult)
def evaluate_candidate_application(
    application_id: int,
    session: Session = Depends(get_session)
):
    """
    Executes automated screening evaluation strictly based on stated job criteria.
    Calculates weighted score, updates application score, and records stage history.
    """
    return evaluate_application(application_id=application_id, session=session)


@router.get("/evaluation/{application_id}", response_model=ScreeningEvaluationResult)
def get_evaluation_details(
    application_id: int,
    session: Session = Depends(get_session)
):
    return evaluate_application(application_id=application_id, session=session)
