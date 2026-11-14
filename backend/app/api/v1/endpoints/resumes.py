from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.resume import ResumeArtifact
from app.models.candidate import Candidate
from app.schemas.recruitment import ResumeArtifactCreate, ResumeArtifactRead

router = APIRouter()


@router.get("/", response_model=list[ResumeArtifactRead])
def get_resume_artifacts(
    candidate_id: Optional[int] = Query(default=None),
    extraction_status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session)
):
    query = select(ResumeArtifact)
    if candidate_id:
        query = query.where(ResumeArtifact.candidate_id == candidate_id)
    if extraction_status:
        query = query.where(ResumeArtifact.extraction_status == extraction_status)
    return session.exec(query.offset(offset).limit(limit)).all()


@router.get("/{resume_id}", response_model=ResumeArtifactRead)
def get_resume_artifact(
    resume_id: int,
    session: Session = Depends(get_session)
):
    artifact = session.get(ResumeArtifact, resume_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Resume artifact not found")
    return artifact


@router.post("/", response_model=ResumeArtifactRead, status_code=201)
def create_resume_artifact(
    artifact_data: ResumeArtifactCreate,
    session: Session = Depends(get_session)
):
    candidate = session.get(Candidate, artifact_data.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    artifact = ResumeArtifact(
        candidate_id=artifact_data.candidate_id,
        file_name=artifact_data.file_name,
        file_type=artifact_data.file_type.upper(),
        file_path=artifact_data.file_path or f"/storage/resumes/{candidate.candidate_code}/{artifact_data.file_name}",
        extraction_status=artifact_data.extraction_status or "PARSED"
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact
