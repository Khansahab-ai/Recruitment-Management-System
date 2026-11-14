from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.candidate import Candidate
from app.models.requisition import JobRequisition
from app.models.application import Application
from app.models.application_stage_history import ApplicationStageHistory

from app.schemas.recruitment import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
    ApplicationHistoryRead
)

router = APIRouter()


# Allowed application stage transitions.
ALLOWED_TRANSITIONS = {
    "APPLIED": {"SCREENING", "REJECTED", "WITHDRAWN"},
    "SCREENING": {"SHORTLISTED", "REJECTED"},
    "SHORTLISTED": {"INTERVIEW", "REJECTED"},
    "INTERVIEW": {"OFFER", "REJECTED"},
    "OFFER": {"REJECTED", "WITHDRAWN"},
    "REJECTED": set(),
    "WITHDRAWN": set()
}


# -------------------------
# CREATE APPLICATION
# -------------------------

@router.post("/", response_model=ApplicationRead, status_code=201)
def create_application(
    application_data: ApplicationCreate,
    session: Session = Depends(get_session)
):
    candidate = session.get(
        Candidate,
        application_data.candidate_id
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    requisition = session.get(
        JobRequisition,
        application_data.requisition_id
    )

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Job requisition not found"
        )

    # Prevent duplicate applications.
    existing = session.exec(
        select(Application).where(
            Application.candidate_id == candidate.candidate_id,
            Application.requisition_id == requisition.requisition_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Candidate has already applied to this requisition"
        )

    if requisition.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Applications are accepted only for OPEN requisitions"
        )

    application_code = (
        f"APP-{requisition.job_code}-{candidate.candidate_code}"
    )

    application = Application(
        application_code=application_code,
        candidate_id=candidate.candidate_id,
        requisition_id=requisition.requisition_id,
        status="APPLIED"
    )

    try:
        session.add(application)
        session.flush()

        # Record the initial application stage.
        history = ApplicationStageHistory(
            application_id=application.application_id,
            previous_status=None,
            new_status="APPLIED",
            changed_by="SYSTEM",
            reason="Application submitted"
        )

        session.add(history)
        session.commit()
        session.refresh(application)

        return application

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Application already exists or violates a database constraint"
        )


# -------------------------
# GET ALL APPLICATIONS
# -------------------------

@router.get("/", response_model=list[ApplicationRead])
def get_applications(
    candidate_id: int | None = Query(default=None),
    requisition_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    statement = select(Application)

    if candidate_id is not None:
        statement = statement.where(
            Application.candidate_id == candidate_id
        )

    if requisition_id is not None:
        statement = statement.where(
            Application.requisition_id == requisition_id
        )

    if status:
        if status not in ALLOWED_TRANSITIONS:
            raise HTTPException(
                status_code=422,
                detail="Invalid application status"
            )

        statement = statement.where(
            Application.status == status
        )

    statement = (
        statement
        .order_by(Application.application_id.desc())
        .offset(offset)
        .limit(limit)
    )

    return session.exec(statement).all()


# -------------------------
# GET SINGLE APPLICATION
# -------------------------

@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: int,
    session: Session = Depends(get_session)
):
    application = session.get(Application, application_id)

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application


# -------------------------
# UPDATE APPLICATION STATUS
# -------------------------

@router.patch("/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int,
    update_data: ApplicationStatusUpdate,
    session: Session = Depends(get_session)
):
    application = session.get(Application, application_id)

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    old_status = application.status
    new_status = update_data.status

    allowed_next = ALLOWED_TRANSITIONS.get(old_status, set())

    if new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {old_status} to {new_status}"
        )

    try:
        application.status = new_status

        history = ApplicationStageHistory(
            application_id=application.application_id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=update_data.changed_by or "SYSTEM",
            reason=update_data.reason
        )

        session.add(application)
        session.add(history)

        session.commit()
        session.refresh(application)

        return application

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not update application status"
        )


# -------------------------
# GET APPLICATION HISTORY
# -------------------------

@router.get(
    "/{application_id}/history",
    response_model=list[ApplicationHistoryRead]
)
def get_application_history(
    application_id: int,
    session: Session = Depends(get_session)
):
    application = session.get(Application, application_id)

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    history = session.exec(
        select(ApplicationStageHistory)
        .where(
            ApplicationStageHistory.application_id == application_id
        )
        .order_by(ApplicationStageHistory.changed_at)
    ).all()

    return history