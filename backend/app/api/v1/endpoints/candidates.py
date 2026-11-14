from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.candidate import Candidate
from app.schemas.recruitment import CandidateCreate, CandidateRead

router = APIRouter()


@router.post("/", response_model=CandidateRead, status_code=201)
def create_candidate(
    candidate_data: CandidateCreate,
    session: Session = Depends(get_session)
):
    email = str(candidate_data.email).strip().lower()

    # Check for an existing email.
    existing = session.exec(
        select(Candidate).where(Candidate.email == email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A candidate with this email already exists"
        )

    try:
        # Reserve the next candidate ID.
        candidate_id = session.execute(
            text("""
                SELECT nextval(
                    pg_get_serial_sequence(
                        'public.candidate',
                        'candidate_id'
                    )
                )
            """)
        ).scalar_one()

        candidate = Candidate(
            candidate_id=candidate_id,
            candidate_code=f"CAND-{candidate_id:06d}",
            full_name=candidate_data.full_name.strip(),
            email=email,
            phone=candidate_data.phone,
            education=candidate_data.education,
            total_experience=candidate_data.total_experience
        )

        session.add(candidate)
        session.commit()
        session.refresh(candidate)

        return candidate

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Candidate could not be created due to a database conflict"
        )


@router.get("/", response_model=list[CandidateRead])
def get_candidates(
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    statement = select(Candidate)

    if search:
        statement = statement.where(
            Candidate.full_name.ilike(f"%{search}%")
            | Candidate.email.ilike(f"%{search}%")
            | Candidate.candidate_code.ilike(f"%{search}%")
        )

    statement = (
        statement
        .order_by(Candidate.candidate_id.desc())
        .offset(offset)
        .limit(limit)
    )

    return session.exec(statement).all()


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: int,
    session: Session = Depends(get_session)
):
    candidate = session.get(Candidate, candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate