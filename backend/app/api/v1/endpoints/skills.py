from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import Optional

from app.db.session import get_session
from app.models.skill import Skill
from app.models.candidate import Candidate
from app.models.candidate_skill import CandidateSkill
from app.schemas.recruitment import (
    SkillCreate,
    SkillRead,
    CandidateSkillCreate,
    CandidateSkillRead
)

router = APIRouter()


@router.get("/", response_model=list[SkillRead])
def get_skills(
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session)
):
    query = select(Skill)
    if category:
        query = query.where(Skill.category == category)
    return session.exec(query.limit(limit)).all()


@router.post("/", response_model=SkillRead, status_code=201)
def create_skill(
    skill_data: SkillCreate,
    session: Session = Depends(get_session)
):
    existing = session.exec(select(Skill).where(Skill.skill_name == skill_data.skill_name)).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Skill '{skill_data.skill_name}' already exists")

    skill = Skill(skill_name=skill_data.skill_name, category=skill_data.category)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.get("/candidates/{candidate_id}", response_model=list[CandidateSkillRead])
def get_candidate_skills(
    candidate_id: int,
    session: Session = Depends(get_session)
):
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    items = session.exec(
        select(CandidateSkill).where(CandidateSkill.candidate_id == candidate_id)
    ).all()

    result = []
    for item in items:
        skill = session.get(Skill, item.skill_id)
        result.append(CandidateSkillRead(
            id=item.id,
            candidate_id=item.candidate_id,
            skill_id=item.skill_id,
            proficiency=item.proficiency,
            skill_name=skill.skill_name if skill else None
        ))
    return result


@router.post("/candidates/{candidate_id}", response_model=CandidateSkillRead, status_code=201)
def add_candidate_skill(
    candidate_id: int,
    skill_assignment: CandidateSkillCreate,
    session: Session = Depends(get_session)
):
    candidate = session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    skill = session.get(Skill, skill_assignment.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = session.exec(
        select(CandidateSkill).where(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_assignment.skill_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill already assigned to candidate")

    cs = CandidateSkill(
        candidate_id=candidate_id,
        skill_id=skill_assignment.skill_id,
        proficiency=skill_assignment.proficiency
    )
    session.add(cs)
    session.commit()
    session.refresh(cs)
    return CandidateSkillRead(
        id=cs.id,
        candidate_id=cs.candidate_id,
        skill_id=cs.skill_id,
        proficiency=cs.proficiency,
        skill_name=skill.skill_name
    )
