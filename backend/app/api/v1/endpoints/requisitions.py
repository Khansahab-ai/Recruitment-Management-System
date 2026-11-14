from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.department import Department
from app.models.requisition import JobRequisition
from app.schemas.recruitment import (
    RequisitionCreate,
    RequisitionUpdate,
    RequisitionRead
)

router = APIRouter()


# -------------------------
# CREATE REQUISITION
# -------------------------

@router.post("/", response_model=RequisitionRead, status_code=201)
def create_requisition(
    requisition_data: RequisitionCreate,
    session: Session = Depends(get_session)
):
    # Check department exists.
    department = session.get(
        Department,
        requisition_data.department_id
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    # Validate salary range.
    if requisition_data.max_salary < requisition_data.min_salary:
        raise HTTPException(
            status_code=422,
            detail="Maximum salary cannot be less than minimum salary"
        )

    try:
        # Reserve the next PostgreSQL primary key.
        next_id = session.execute(
            text("""
                SELECT nextval(
                    pg_get_serial_sequence(
                        'public.jobrequisition',
                        'requisition_id'
                    )
                )
            """)
        ).scalar_one()

        # Generate business ID.
        current_year = datetime.now(timezone.utc).year

        job_code = f"REQ-{current_year}-{next_id:06d}"

        requisition = JobRequisition(
            requisition_id=next_id,
            job_code=job_code,
            job_title=requisition_data.job_title,
            department_id=requisition_data.department_id,
            openings=requisition_data.openings,
            min_salary=requisition_data.min_salary,
            max_salary=requisition_data.max_salary,
            experience_required=requisition_data.experience_required,
            status="DRAFT"
        )

        session.add(requisition)
        session.commit()
        session.refresh(requisition)

        return requisition

    except IntegrityError as error:
        session.rollback()

        print("DATABASE INTEGRITY ERROR:", error.orig)

        raise HTTPException(
            status_code=409,
            detail=f"Database conflict: {str(error.orig)}"
        )


# -------------------------
# GET ALL REQUISITIONS
# -------------------------

@router.get("/", response_model=list[RequisitionRead])
def get_requisitions(
    status: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    session: Session = Depends(get_session)
):
    statement = select(JobRequisition)

    if status:
        allowed_statuses = ["DRAFT", "OPEN", "ON_HOLD", "CLOSED"]

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=422,
                detail="Invalid requisition status"
            )

        statement = statement.where(
            JobRequisition.status == status
        )

    if department_id is not None:
        statement = statement.where(
            JobRequisition.department_id == department_id
        )

    if search:
        statement = statement.where(
            JobRequisition.job_title.ilike(f"%{search}%")
            | JobRequisition.job_code.ilike(f"%{search}%")
        )

    statement = statement.order_by(
        JobRequisition.requisition_id.desc()
    )

    return session.exec(statement).all()


# -------------------------
# GET SINGLE REQUISITION
# -------------------------

@router.get("/{requisition_id}", response_model=RequisitionRead)
def get_requisition(
    requisition_id: int,
    session: Session = Depends(get_session)
):
    requisition = session.get(
        JobRequisition,
        requisition_id
    )

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    return requisition


# -------------------------
# UPDATE REQUISITION
# -------------------------

@router.patch("/{requisition_id}", response_model=RequisitionRead)
def update_requisition(
    requisition_id: int,
    update_data: RequisitionUpdate,
    session: Session = Depends(get_session)
):
    requisition = session.get(
        JobRequisition,
        requisition_id
    )

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    if requisition.status == "CLOSED":
        raise HTTPException(
            status_code=400,
            detail="Closed requisitions cannot be updated"
        )

    updates = update_data.model_dump(exclude_unset=True)

    # Validate department if being changed.
    if "department_id" in updates:
        department = session.get(
            Department,
            updates["department_id"]
        )

        if not department:
            raise HTTPException(
                status_code=404,
                detail="Department not found"
            )

    # Validate the final salary range.
    min_salary = updates.get(
        "min_salary",
        requisition.min_salary
    )

    max_salary = updates.get(
        "max_salary",
        requisition.max_salary
    )

    if max_salary < min_salary:
        raise HTTPException(
            status_code=422,
            detail="Maximum salary cannot be less than minimum salary"
        )

    for key, value in updates.items():
        setattr(requisition, key, value)

    try:
        session.add(requisition)
        session.commit()
        session.refresh(requisition)

        return requisition

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Database constraint violation"
        )


# -------------------------
# CLOSE REQUISITION
# -------------------------

@router.post("/{requisition_id}/close", response_model=RequisitionRead)
def close_requisition(
    requisition_id: int,
    session: Session = Depends(get_session)
):
    requisition = session.get(
        JobRequisition,
        requisition_id
    )

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Requisition not found"
        )

    if requisition.status == "CLOSED":
        raise HTTPException(
            status_code=400,
            detail="Requisition is already closed"
        )

    requisition.status = "CLOSED"

    session.add(requisition)
    session.commit()
    session.refresh(requisition)

    return requisition