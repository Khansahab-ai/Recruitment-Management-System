from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.department import Department
from app.models.requisition import JobRequisition
from app.models.application import Application
from app.models.offer import Offer
from app.schemas.recruitment import (
    FunnelMetricsResponse,
    OperationalKPIsResponse
)
from app.services.analytics_service import (
    get_recruitment_funnel,
    get_operational_kpis
)

router = APIRouter()


@router.get("/funnel", response_model=FunnelMetricsResponse)
def get_funnel_metrics(session: Session = Depends(get_session)):
    """
    Returns recruitment pipeline funnel conversion rates from APPLIED to ACCEPTED.
    """
    return get_recruitment_funnel(session=session)


@router.get("/kpis", response_model=OperationalKPIsResponse)
def get_system_kpis(session: Session = Depends(get_session)):
    """
    Returns measurable evaluation outputs: time-to-hire, acceptance rate, totals.
    """
    return get_operational_kpis(session=session)


@router.get("/departments")
def get_department_breakdown(session: Session = Depends(get_session)):
    """
    Returns requisition, applicant, and offer counts grouped by department.
    """
    departments = session.exec(select(Department)).all()
    results = []

    for dept in departments:
        reqs = session.exec(
            select(JobRequisition).where(JobRequisition.department_id == dept.department_id)
        ).all()
        req_ids = [r.requisition_id for r in reqs]

        app_count = 0
        offer_count = 0
        if req_ids:
            apps = session.exec(
                select(Application).where(Application.requisition_id.in_(req_ids))
            ).all()
            app_count = len(apps)
            app_ids = [a.application_id for a in apps]
            if app_ids:
                offers = session.exec(
                    select(Offer).where(Offer.application_id.in_(app_ids))
                ).all()
                offer_count = len(offers)

        results.append({
            "department_id": dept.department_id,
            "department_name": dept.name,
            "total_requisitions": len(reqs),
            "open_requisitions": len([r for r in reqs if r.status == "OPEN"]),
            "total_applications": app_count,
            "total_offers": offer_count
        })

    return results
