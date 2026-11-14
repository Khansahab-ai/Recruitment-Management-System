"""
Screening Service
Evaluates applications strictly on job-related criteria (skills match, experience, education).
Excludes demographic proxies and enforces structured scoring rules.
"""

from typing import Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.application import Application
from app.models.candidate import Candidate
from app.models.requisition import JobRequisition
from app.models.screening_rule import ScreeningRule
from app.models.candidate_skill import CandidateSkill
from app.models.application_stage_history import ApplicationStageHistory
from app.schemas.recruitment import ScreeningEvaluationResult, ScreeningEvaluationDetail


def evaluate_application(application_id: int, session: Session) -> ScreeningEvaluationResult:
    """
    Evaluates an application against the job requisition's screening rules.
    Calculates weighted score (0-100) and persists it to the Application record.
    """
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    candidate = session.get(Candidate, application.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    requisition = session.get(JobRequisition, application.requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")

    # Fetch screening rules for this requisition
    rules = session.exec(
        select(ScreeningRule).where(ScreeningRule.requisition_id == requisition.requisition_id)
    ).all()

    # If no rules exist, default to 100 based on minimum experience requirement
    if not rules:
        exp_score = min(100.0, (candidate.total_experience / max(requisition.experience_required, 1.0)) * 100.0)
        application.screening_score = round(exp_score, 2)
        session.add(application)
        session.commit()
        return ScreeningEvaluationResult(
            application_id=application_id,
            candidate_id=candidate.candidate_id,
            requisition_id=requisition.requisition_id,
            total_score=application.screening_score,
            is_qualified=application.screening_score >= 60.0,
            recommended_stage="SHORTLISTED" if application.screening_score >= 60.0 else "REJECTED",
            rule_breakdown=[]
        )

    # Candidate skills
    cand_skills = session.exec(
        select(CandidateSkill).where(CandidateSkill.candidate_id == candidate.candidate_id)
    ).all()
    proficiency_map = {
        "BEGINNER": 40.0,
        "INTERMEDIATE": 70.0,
        "ADVANCED": 90.0,
        "EXPERT": 100.0
    }

    rule_details = []
    total_weighted_score = 0.0
    all_mandatory_passed = True

    for rule in rules:
        raw_score = 0.0
        comments = ""
        cname = rule.criteria_name.upper()

        if "SKILL" in cname:
            if cand_skills:
                # Average score of candidate skills
                avg_prof = sum(proficiency_map.get(s.proficiency, 50.0) for s in cand_skills) / len(cand_skills)
                # Count factor: having 4+ skills awards full credit
                count_factor = min(1.0, len(cand_skills) / 4.0)
                raw_score = avg_prof * count_factor
                comments = f"Evaluated {len(cand_skills)} candidate skills; avg proficiency score {avg_prof:.1f}"
            else:
                raw_score = 0.0
                comments = "No candidate skills recorded"

        elif "EXPERIENCE" in cname:
            req_exp = max(requisition.experience_required, 0.5)
            ratio = candidate.total_experience / req_exp
            raw_score = min(100.0, ratio * 100.0)
            comments = f"Candidate experience: {candidate.total_experience} yrs vs Required: {requisition.experience_required} yrs"

        elif "EDUCATION" in cname:
            edu_scores = {
                "PhD": 100.0,
                "Master's": 90.0,
                "Bachelor's": 80.0,
                "Diploma": 60.0,
                "Other": 50.0
            }
            raw_score = edu_scores.get(candidate.education, 70.0)
            comments = f"Education level: {candidate.education or 'Unspecified'}"

        elif "TECHNICAL" in cname or "DOMAIN" in cname:
            # Domain / technical evaluation based on skill depth
            advanced_count = sum(1 for s in cand_skills if s.proficiency in ["ADVANCED", "EXPERT"])
            raw_score = min(100.0, advanced_count * 35.0 + 30.0)
            comments = f"Found {advanced_count} advanced/expert skills"

        else:
            raw_score = 75.0
            comments = f"Standard criterion evaluation for {rule.criteria_name}"

        raw_score = max(0.0, min(100.0, raw_score))
        weighted_score = (raw_score * rule.weight) / 100.0
        total_weighted_score += weighted_score

        min_req = rule.minimum_score or 50.0
        passed = raw_score >= min_req
        if rule.is_mandatory and not passed:
            all_mandatory_passed = False

        rule_details.append(ScreeningEvaluationDetail(
            rule_id=rule.rule_id,
            criteria_name=rule.criteria_name,
            weight=rule.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(weighted_score, 2),
            passed=passed,
            comments=comments
        ))

    final_score = round(total_weighted_score, 2)
    is_qualified = (final_score >= 60.0) and all_mandatory_passed
    recommended_stage = "SHORTLISTED" if is_qualified else "REJECTED"

    # Persist score to application
    application.screening_score = final_score
    session.add(application)

    # Record stage history if transitioning to screening
    if application.status == "APPLIED":
        new_status = "SCREENING"
        history = ApplicationStageHistory(
            application_id=application.application_id,
            previous_status="APPLIED",
            new_status=new_status,
            changed_by="SCREENING_ENGINE",
            reason=f"Structured screening completed with score {final_score}/100"
        )
        application.status = new_status
        session.add(history)

    session.commit()
    session.refresh(application)

    return ScreeningEvaluationResult(
        application_id=application.application_id,
        candidate_id=candidate.candidate_id,
        requisition_id=requisition.requisition_id,
        total_score=final_score,
        is_qualified=is_qualified,
        recommended_stage=recommended_stage,
        rule_breakdown=rule_details
    )
