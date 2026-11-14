"""
Interview Service
Handles interview scheduling, panel assignment, and schedule conflict prevention.
Ensures interviewers are not double-booked for overlapping time slots.
"""

from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.interview import Interview
from app.models.interviewer import Interviewer
from app.models.interview_assignment import InterviewAssignment
from app.models.application import Application
from app.models.application_stage_history import ApplicationStageHistory


def check_interviewer_availability(
    interviewer_id: int,
    scheduled_start: datetime,
    scheduled_end: datetime,
    exclude_interview_id: int | None,
    session: Session
) -> tuple[bool, str]:
    """
    Checks if an interviewer is available for a specified time range.
    Returns (True, "Available") or (False, "Conflict description").
    """
    interviewer = session.get(Interviewer, interviewer_id)
    if not interviewer:
        return False, "Interviewer not found"
    if not interviewer.is_active:
        return False, f"Interviewer {interviewer.full_name} is inactive"

    # Query all active interviews assigned to this interviewer
    query = (
        select(Interview)
        .join(InterviewAssignment, InterviewAssignment.interview_id == Interview.interview_id)
        .where(
            InterviewAssignment.interviewer_id == interviewer_id,
            Interview.status.in_(["SCHEDULED", "RESCHEDULED"])
        )
    )
    if exclude_interview_id is not None:
        query = query.where(Interview.interview_id != exclude_interview_id)

    assigned_interviews = session.exec(query).all()

    for existing in assigned_interviews:
        # Check overlap: (StartA < EndB) and (EndA > StartB)
        if existing.scheduled_start < scheduled_end and existing.scheduled_end > scheduled_start:
            return False, (
                f"Schedule conflict: Interviewer {interviewer.full_name} is already assigned to "
                f"interview {existing.interview_code} from {existing.scheduled_start.isoformat()} "
                f"to {existing.scheduled_end.isoformat()}"
            )

    return True, "Available"


def assign_interviewer_to_interview(
    interview_id: int,
    interviewer_id: int,
    session: Session,
    enforce_availability: bool = True
) -> InterviewAssignment:
    """
    Assigns an interviewer to an interview round with availability validation.
    """
    interview = session.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interviewer = session.get(Interviewer, interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")

    # Check for duplicate assignment to the same interview
    existing_assignment = session.exec(
        select(InterviewAssignment).where(
            InterviewAssignment.interview_id == interview_id,
            InterviewAssignment.interviewer_id == interviewer_id
        )
    ).first()
    if existing_assignment:
        raise HTTPException(status_code=409, detail="Interviewer is already assigned to this interview")

    # Enforce schedule conflict check
    if enforce_availability:
        is_avail, reason = check_interviewer_availability(
            interviewer_id=interviewer_id,
            scheduled_start=interview.scheduled_start,
            scheduled_end=interview.scheduled_end,
            exclude_interview_id=interview_id,
            session=session
        )
        if not is_avail:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot assign interviewer: {reason}"
            )

    assignment = InterviewAssignment(
        interview_id=interview_id,
        interviewer_id=interviewer_id
    )
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment
