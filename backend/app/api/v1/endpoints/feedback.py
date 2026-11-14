from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.feedback import Feedback
from app.models.interview import Interview
from app.models.interviewer import Interviewer
from app.models.interview_assignment import InterviewAssignment
from app.schemas.recruitment import (
    FeedbackCreate,
    FeedbackRead,
    FeedbackCompletenessCheck
)

router = APIRouter()


@router.get("/", response_model=list[FeedbackRead])
def get_feedback_records(
    interview_id: Optional[int] = Query(default=None),
    interviewer_id: Optional[int] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session)
):
    query = select(Feedback)
    if interview_id is not None:
        query = query.where(Feedback.interview_id == interview_id)
    if interviewer_id is not None:
        query = query.where(Feedback.interviewer_id == interviewer_id)
    return session.exec(query.order_by(Feedback.feedback_id.desc()).limit(limit)).all()


@router.post("/", response_model=FeedbackRead, status_code=201)
def submit_feedback(
    feedback_data: FeedbackCreate,
    session: Session = Depends(get_session)
):
    interview = session.get(Interview, feedback_data.interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interviewer = session.get(Interviewer, feedback_data.interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    # Verify that the interviewer is assigned to this interview
    assignment = session.exec(
        select(InterviewAssignment).where(
            InterviewAssignment.interview_id == feedback_data.interview_id,
            InterviewAssignment.interviewer_id == feedback_data.interviewer_id
        )
    ).first()
    if not assignment:
        raise HTTPException(
            status_code=400,
            detail=f"Interviewer {interviewer.full_name} is not assigned to interview {interview.interview_code}"
        )

    # Check for duplicate feedback
    existing = session.exec(
        select(Feedback).where(
            Feedback.interview_id == feedback_data.interview_id,
            Feedback.interviewer_id == feedback_data.interviewer_id
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Interviewer {interviewer.full_name} has already submitted feedback for this interview"
        )

    # Calculate overall weighted average score
    overall = round(
        (feedback_data.technical_score * 0.4)
        + (feedback_data.problem_solving_score * 0.4)
        + (feedback_data.communication_score * 0.2),
        2
    )

    feedback_code = f"FB-{feedback_data.interview_id:06d}-{feedback_data.interviewer_id:06d}"

    feedback = Feedback(
        feedback_code=feedback_code,
        interview_id=feedback_data.interview_id,
        interviewer_id=feedback_data.interviewer_id,
        technical_score=feedback_data.technical_score,
        problem_solving_score=feedback_data.problem_solving_score,
        communication_score=feedback_data.communication_score,
        overall_score=overall,
        recommendation=feedback_data.recommendation,
        comments=feedback_data.comments
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    return feedback


@router.get("/completeness/{interview_id}", response_model=FeedbackCompletenessCheck)
def check_feedback_completeness(
    interview_id: int,
    session: Session = Depends(get_session)
):
    interview = session.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    assignments = session.exec(
        select(InterviewAssignment).where(InterviewAssignment.interview_id == interview_id)
    ).all()
    feedbacks = session.exec(
        select(Feedback).where(Feedback.interview_id == interview_id)
    ).all()

    assigned_ids = {a.interviewer_id for a in assignments}
    submitted_ids = {f.interviewer_id for f in feedbacks}
    missing_ids = list(assigned_ids - submitted_ids)

    return FeedbackCompletenessCheck(
        interview_id=interview_id,
        application_id=interview.application_id,
        expected_feedback_count=len(assigned_ids),
        submitted_feedback_count=len(submitted_ids),
        is_complete=(len(missing_ids) == 0 and len(assigned_ids) > 0),
        missing_interviewer_ids=missing_ids
    )
