from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.department import Department
from app.schemas.recruitment import DepartmentCreate, DepartmentRead

router = APIRouter()


@router.post("/", response_model=DepartmentRead, status_code=201)
def create_department(
    department_data: DepartmentCreate,
    session: Session = Depends(get_session)
):
    # Check whether department already exists.
    existing = session.exec(
        select(Department).where(
            Department.name == department_data.name
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Department already exists"
        )

    department = Department(**department_data.model_dump())

    session.add(department)

    try:
        session.commit()
        session.refresh(department)
        return department

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Department name must be unique"
        )


@router.get("/", response_model=list[DepartmentRead])
def get_departments(
    session: Session = Depends(get_session)
):
    departments = session.exec(
        select(Department).order_by(Department.department_id)
    ).all()

    return departments


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(
    department_id: int,
    session: Session = Depends(get_session)
):
    department = session.get(Department, department_id)

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department