from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.offer import Offer
from app.models.offer_approval_history import OfferApprovalHistory
from app.models.application import Application
from app.schemas.recruitment import (
    OfferCreate,
    OfferRead,
    OfferApprovalCreate,
    OfferApprovalRead,
    OfferStatusUpdate
)
from app.services.offer_service import (
    create_job_offer,
    process_offer_approval
)

router = APIRouter()


@router.get("/", response_model=list[OfferRead])
def get_offers(
    application_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    query = select(Offer)
    if application_id is not None:
        query = query.where(Offer.application_id == application_id)
    if status:
        query = query.where(Offer.status == status)

    offers = session.exec(query.order_by(Offer.offer_id.desc()).offset(offset).limit(limit)).all()

    result = []
    for off in offers:
        approvals = session.exec(
            select(OfferApprovalHistory)
            .where(OfferApprovalHistory.offer_id == off.offer_id)
            .order_by(OfferApprovalHistory.approved_at)
        ).all()
        result.append(OfferRead(
            offer_id=off.offer_id,
            offer_code=off.offer_code,
            application_id=off.application_id,
            offered_salary=off.offered_salary,
            joining_date=off.joining_date,
            status=off.status,
            created_at=off.created_at,
            approvals=approvals
        ))
    return result


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(
    offer_id: int,
    session: Session = Depends(get_session)
):
    off = session.get(Offer, offer_id)
    if not off:
        raise HTTPException(status_code=404, detail="Offer not found")

    approvals = session.exec(
        select(OfferApprovalHistory)
        .where(OfferApprovalHistory.offer_id == off.offer_id)
        .order_by(OfferApprovalHistory.approved_at)
    ).all()

    return OfferRead(
        offer_id=off.offer_id,
        offer_code=off.offer_code,
        application_id=off.application_id,
        offered_salary=off.offered_salary,
        joining_date=off.joining_date,
        status=off.status,
        created_at=off.created_at,
        approvals=approvals
    )


@router.post("/", response_model=OfferRead, status_code=201)
def propose_offer(
    offer_data: OfferCreate,
    session: Session = Depends(get_session)
):
    """
    Creates an offer with strict salary band compliance checking.
    Rejects proposals outside the requisition's approved min and max salary band.
    """
    offer = create_job_offer(offer_data=offer_data, session=session)
    return get_offer(offer_id=offer.offer_id, session=session)


@router.post("/{offer_id}/approve", response_model=OfferRead)
def approve_or_reject_offer(
    offer_id: int,
    approval_data: OfferApprovalCreate,
    session: Session = Depends(get_session)
):
    """
    Submits an executive/committee approval decision for a pending offer.
    """
    process_offer_approval(offer_id=offer_id, approval_data=approval_data, session=session)
    return get_offer(offer_id=offer_id, session=session)


@router.patch("/{offer_id}/status", response_model=OfferRead)
def update_offer_status(
    offer_id: int,
    status_data: OfferStatusUpdate,
    session: Session = Depends(get_session)
):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    allowed = {
        "PENDING_APPROVAL": {"APPROVED", "REJECTED"},
        "APPROVED": {"SENT", "REJECTED"},
        "SENT": {"ACCEPTED", "DECLINED"},
        "ACCEPTED": set(),
        "DECLINED": set(),
        "REJECTED": set()
    }
    if status_data.status not in allowed.get(offer.status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition offer from {offer.status} to {status_data.status}"
        )

    offer.status = status_data.status
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return get_offer(offer_id=offer_id, session=session)


@router.get("/{offer_id}/history", response_model=list[OfferApprovalRead])
def get_offer_approval_history(
    offer_id: int,
    session: Session = Depends(get_session)
):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    return session.exec(
        select(OfferApprovalHistory)
        .where(OfferApprovalHistory.offer_id == offer_id)
        .order_by(OfferApprovalHistory.approved_at)
    ).all()
