import json
from pathlib import Path
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.recruitment import ExceptionAuditReport
from app.services.audit_service import run_system_audit

router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[4]
GROUND_TRUTH_DIR = ROOT_DIR / "data" / "ground_truth"


@router.get("/detect", response_model=ExceptionAuditReport)
def detect_system_exceptions(session: Session = Depends(get_session)):
    """
    Executes automated anomaly detection to expose policy violations and exceptions:
    - Interview scheduled for unavailable interviewer
    - Duplicate applications
    - Feedback missing but stage advanced
    - Offer salary outside approved band
    - Role closed with active applications
    """
    return run_system_audit(session=session)


@router.get("/ground-truth")
def get_ground_truth_cases():
    """
    Exposes the 5 ground-truth edge cases and their expected outcomes.
    """
    gt_file = GROUND_TRUTH_DIR / "ground_truth.json"
    if gt_file.exists():
        with open(gt_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback to individual files
    results = []
    for fname in [
        "unavailable_interviewer_case.json",
        "duplicate_application_case.json",
        "missing_feedback_case.json",
        "salary_outside_band_case.json",
        "closed_requisition_active_applications.json"
    ]:
        p = GROUND_TRUTH_DIR / fname
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                results.append(json.load(f))
    return results
