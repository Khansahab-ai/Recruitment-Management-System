from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.interview import Interview
from app.models.interviewer import Interviewer
from app.models.interview_assignment import InterviewAssignment
from app.models.application import Application
from app.models.application_stage_history import ApplicationStageHistory
from app.schemas.recruitment import (
    InterviewCreate,
    InterviewUpdate,
    InterviewRead,
    InterviewAssignmentCreate,
    InterviewAssignmentRead
)
from app.services.interview_service import assign_interviewer_to_interview

router = APIRouter()


@router.get("/", response_model=list[InterviewRead])
def get_interviews(
    application_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    query = select(Interview)
    if application_id is not None:
        query = query.where(Interview.application_id == application_id)
    if status:
        query = query.where(Interview.status == status)

    interviews = session.exec(query.order_by(Interview.interview_id.desc()).offset(offset).limit(limit)).all()

    result = []
    for intv in interviews:
        assignments = session.exec(
            select(InterviewAssignment).where(InterviewAssignment.interview_id == intv.interview_id)
        ).all()
        assign_reads = []
        for a in assignments:
            ivr = session.get(Interviewer, a.interviewer_id)
            assign_reads.append(InterviewAssignmentRead(
                assignment_id=a.assignment_id,
                interview_id=a.interview_id,
                interviewer_id=a.interviewer_id,
                interviewer_name=ivr.full_name if ivr else None,
                interviewer_email=ivr.email if ivr else None
            ))

        result.append(InterviewRead(
            interview_id=intv.interview_id,
            interview_code=intv.interview_code,
            application_id=intv.application_id,
            round_name=intv.round_name,
            scheduled_start=intv.scheduled_start,
            scheduled_end=intv.scheduled_end,
            status=intv.status,
            created_at=intv.created_at,
            assignments=assign_reads
        ))
    return result


@router.get("/{interview_id}", response_model=InterviewRead)
def get_interview(
    interview_id: int,
    session: Session = Depends(get_session)
):
    intv = session.get(Interview, interview_id)
    if not intv:
        raise HTTPException(status_code=404, detail="Interview not found")

    assignments = session.exec(
        select(InterviewAssignment).where(InterviewAssignment.interview_id == intv.interview_id)
    ).all()
    assign_reads = []
    for a in assignments:
        ivr = session.get(Interviewer, a.interviewer_id)
        assign_reads.append(InterviewAssignmentRead(
            assignment_id=a.assignment_id,
            interview_id=a.interview_id,
            interviewer_id=a.interviewer_id,
            interviewer_name=ivr.full_name if ivr else None,
            interviewer_email=ivr.email if ivr else None
        ))

    return InterviewRead(
        interview_id=intv.interview_id,
        interview_code=intv.interview_code,
        application_id=intv.application_id,
        round_name=intv.round_name,
        scheduled_start=intv.scheduled_start,
        scheduled_end=intv.scheduled_end,
        status=intv.status,
        created_at=intv.created_at,
        assignments=assign_reads
    )


@router.post("/", response_model=InterviewRead, status_code=201)
def schedule_interview(
    interview_data: InterviewCreate,
    session: Session = Depends(get_session)
):
    application = session.get(Application, interview_data.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if interview_data.scheduled_end <= interview_data.scheduled_start:
        raise HTTPException(status_code=422, detail="Interview end time must be strictly after start time")

    current_year = datetime.now(timezone.utc).year
    total = session.exec(select(Interview)).all()
    next_id = len(total) + 1
    code = f"INT-{current_year}-{next_id:06d}"

    interview = Interview(
        interview_code=code,
        application_id=interview_data.application_id,
        round_name=interview_data.round_name,
        scheduled_start=interview_data.scheduled_start,
        scheduled_end=interview_data.scheduled_end,
        status="SCHEDULED"
    )
    session.add(interview)

    # Progress application stage to INTERVIEW if currently SHORTLISTED or SCREENING
    if application.status in ["SHORTLISTED", "SCREENING"]:
        prev = application.status
        application.status = "INTERVIEW"
        history = ApplicationStageHistory(
            application_id=application.application_id,
            previous_status=prev,
            new_status="INTERVIEW",
            changed_by="INTERVIEW_COORDINATOR",
            reason=f"Interview {code} scheduled ({interview_data.round_name})"
        )
        session.add(application)
        session.add(history)

    session.commit()
    session.refresh(interview)

    return InterviewRead(
        interview_id=interview.interview_id,
        interview_code=interview.interview_code,
        application_id=interview.application_id,
        round_name=interview.round_name,
        scheduled_start=interview.scheduled_start,
        scheduled_end=interview.scheduled_end,
        status=interview.status,
        created_at=interview.created_at,
        assignments=[]
    )


@router.patch("/{interview_id}", response_model=InterviewRead)
def update_interview(
    interview_id: int,
    update_data: InterviewUpdate,
    session: Session = Depends(get_session)
):
    interview = session.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if update_data.round_name is not None:
        interview.round_name = update_data.round_name
    if update_data.scheduled_start is not None:
        interview.scheduled_start = update_data.scheduled_start
    if update_data.scheduled_end is not None:
        interview.scheduled_end = update_data.scheduled_end
    if update_data.status is not None:
        interview.status = update_data.status

    if interview.scheduled_end <= interview.scheduled_start:
        raise HTTPException(status_code=422, detail="Interview end time must be after start time")

    session.add(interview)
    session.commit()
    session.refresh(interview)
    return get_interview(interview_id=interview_id, session=session)


@router.post("/{interview_id}/assign", response_model=InterviewAssignmentRead, status_code=201)
def assign_panel_member(
    interview_id: int,
    assignment_data: InterviewAssignmentCreate,
    enforce_conflict_check: bool = Query(default=True),
    session: Session = Depends(get_session)
):
    """
    Assigns an interviewer to the interview panel.
    Enforces schedule conflict prevention unless explicitly bypassed for testing.
    """
    assignment = assign_interviewer_to_interview(
        interview_id=interview_id,
        interviewer_id=assignment_data.interviewer_id,
        session=session,
        enforce_availability=enforce_conflict_check
    )
    ivr = session.get(Interviewer, assignment.interviewer_id)
    return InterviewAssignmentRead(
        assignment_id=assignment.assignment_id,
        interview_id=assignment.interview_id,
        interviewer_id=assignment.interviewer_id,
        interviewer_name=ivr.full_name if ivr else None,
        interviewer_email=ivr.email if ivr else None
    )
