"""
Offer Service
Handles offer proposals, salary band validation against requisition bounds,
and multi-tier approval histories.
"""

from datetime import datetime, timezone
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.offer import Offer
from app.models.offer_approval_history import OfferApprovalHistory
from app.models.application import Application
from app.models.requisition import JobRequisition
from app.models.application_stage_history import ApplicationStageHistory
from app.schemas.recruitment import OfferCreate, OfferApprovalCreate


def validate_offer_salary(application_id: int, offered_salary: float, session: Session) -> JobRequisition:
    """
    Validates that the offered salary falls strictly within the job requisition's approved min and max salary band.
    """
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    requisition = session.get(JobRequisition, application.requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")

    if offered_salary < requisition.min_salary or offered_salary > requisition.max_salary:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Offered salary {offered_salary:,.2f} is outside the approved salary band "
                f"[{requisition.min_salary:,.2f} - {requisition.max_salary:,.2f}] "
                f"for requisition {requisition.job_code} ({requisition.job_title})"
            )
        )

    return requisition


def create_job_offer(offer_data: OfferCreate, session: Session) -> Offer:
    """
    Proposes a new job offer with strict salary band compliance check.
    """
    # Verify application status allows offer
    application = session.get(Application, offer_data.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status not in ["INTERVIEW", "SHORTLISTED", "OFFER"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot make offer to candidate in stage '{application.status}'. Candidate must be in INTERVIEW stage."
        )

    # Check for existing active offer on this application
    existing_offer = session.exec(
        select(Offer).where(
            Offer.application_id == offer_data.application_id,
            Offer.status.in_(["PENDING_APPROVAL", "APPROVED", "SENT", "ACCEPTED"])
        )
    ).first()
    if existing_offer:
        raise HTTPException(status_code=409, detail=f"An active offer {existing_offer.offer_code} already exists for this application")

    # Salary band validation (enforces EDGE-04 rule)
    requisition = validate_offer_salary(offer_data.application_id, offer_data.offered_salary, session)

    # Deterministic offer code
    current_year = datetime.now(timezone.utc).year
    count = session.exec(select(Offer)).all()
    next_id = len(count) + 1
    offer_code = f"OFF-{current_year}-{next_id:06d}"

    offer = Offer(
        offer_code=offer_code,
        application_id=offer_data.application_id,
        offered_salary=offer_data.offered_salary,
        joining_date=offer_data.joining_date,
        status="PENDING_APPROVAL"
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)

    # Record initial pending approval event in OfferApprovalHistory
    initial_approval = OfferApprovalHistory(
        offer_id=offer.offer_id,
        approver_id=None,
        decision="PENDING",
        comments="Offer submitted for executive approval",
        approved_at=datetime.now(timezone.utc)
    )
    session.add(initial_approval)
    session.commit()

    return offer


def process_offer_approval(offer_id: int, approval_data: OfferApprovalCreate, session: Session) -> Offer:
    """
    Records an approver's decision (APPROVED or REJECTED) and updates the offer and application stage.
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Offer is not pending approval (current status: {offer.status})")

    # Record approval event
    approval = OfferApprovalHistory(
        offer_id=offer.offer_id,
        approver_id=approval_data.approver_id,
        decision=approval_data.decision,
        comments=approval_data.comments or f"Decision {approval_data.decision} recorded",
        approved_at=datetime.now(timezone.utc)
    )
    session.add(approval)

    # Update offer status
    if approval_data.decision == "APPROVED":
        offer.status = "APPROVED"
        # Progress application to OFFER stage
        app = session.get(Application, offer.application_id)
        if app and app.status != "OFFER":
            history = ApplicationStageHistory(
                application_id=app.application_id,
                previous_status=app.status,
                new_status="OFFER",
                changed_by=f"APPROVER_{approval_data.approver_id or 'ADMIN'}",
                reason="Offer approved by hiring committee"
            )
            app.status = "OFFER"
            session.add(app)
            session.add(history)
    else:
        offer.status = "REJECTED"

    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer
