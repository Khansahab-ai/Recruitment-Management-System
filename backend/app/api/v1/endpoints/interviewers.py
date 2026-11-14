from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.interviewer import Interviewer
from app.models.department import Department
from app.models.interview import Interview
from app.models.interview_assignment import InterviewAssignment
from app.schemas.recruitment import (
    InterviewerCreate,
    InterviewerUpdate,
    InterviewerRead,
    InterviewRead
)

router = APIRouter()


@router.get("/", response_model=list[InterviewerRead])
def get_interviewers(
    department_id: Optional[int] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session)
):
    query = select(Interviewer)
    if department_id is not None:
        query = query.where(Interviewer.department_id == department_id)
    if is_active is not None:
        query = query.where(Interviewer.is_active == is_active)
    return session.exec(query.limit(limit)).all()


@router.get("/{interviewer_id}", response_model=InterviewerRead)
def get_interviewer(
    interviewer_id: int,
    session: Session = Depends(get_session)
):
    interviewer = session.get(Interviewer, interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    return interviewer


@router.post("/", response_model=InterviewerRead, status_code=201)
def create_interviewer(
    interviewer_data: InterviewerCreate,
    session: Session = Depends(get_session)
):
    dept = session.get(Department, interviewer_data.department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    existing_email = session.exec(select(Interviewer).where(Interviewer.email == interviewer_data.email)).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Interviewer email already registered")

    all_ivrs = session.exec(select(Interviewer)).all()
    next_id = len(all_ivrs) + 1
    code = f"IVR-{next_id:06d}"

    interviewer = Interviewer(
        interviewer_code=code,
        full_name=interviewer_data.full_name,
        email=interviewer_data.email,
        department_id=interviewer_data.department_id,
        is_active=interviewer_data.is_active
    )
    session.add(interviewer)
    session.commit()
    session.refresh(interviewer)
    return interviewer


@router.patch("/{interviewer_id}", response_model=InterviewerRead)
def update_interviewer(
    interviewer_id: int,
    update_data: InterviewerUpdate,
    session: Session = Depends(get_session)
):
    interviewer = session.get(Interviewer, interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    if update_data.full_name is not None:
        interviewer.full_name = update_data.full_name
    if update_data.email is not None:
        interviewer.email = update_data.email
    if update_data.department_id is not None:
        dept = session.get(Department, update_data.department_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        interviewer.department_id = update_data.department_id
    if update_data.is_active is not None:
        interviewer.is_active = update_data.is_active

    session.add(interviewer)
    session.commit()
    session.refresh(interviewer)
    return interviewer


@router.get("/{interviewer_id}/schedule")
def get_interviewer_schedule(
    interviewer_id: int,
    session: Session = Depends(get_session)
):
    interviewer = session.get(Interviewer, interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    interviews = session.exec(
        select(Interview)
        .join(InterviewAssignment, InterviewAssignment.interview_id == Interview.interview_id)
        .where(InterviewAssignment.interviewer_id == interviewer_id)
        .order_by(Interview.scheduled_start)
    ).all()

    return {
        "interviewer_id": interviewer.interviewer_id,
        "interviewer_code": interviewer.interviewer_code,
        "full_name": interviewer.full_name,
        "is_active": interviewer.is_active,
        "total_scheduled_interviews": len(interviews),
        "scheduled_rounds": [
            {
                "interview_id": i.interview_id,
                "interview_code": i.interview_code,
                "round_name": i.round_name,
                "start": i.scheduled_start,
                "end": i.scheduled_end,
                "status": i.status
            }
            for i in interviews
        ]
    }
