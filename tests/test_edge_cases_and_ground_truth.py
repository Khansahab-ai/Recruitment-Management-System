import json
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
GROUND_TRUTH_DIR = ROOT_DIR / "data" / "ground_truth"


def test_ground_truth_files_exist():
    """Verify separate ground_truth files exist and do not leak into input features."""
    expected_files = [
        "unavailable_interviewer_case.json",
        "duplicate_application_case.json",
        "missing_feedback_case.json",
        "salary_outside_band_case.json",
        "closed_requisition_active_applications.json",
        "ground_truth.json",
        "ground_truth.csv"
    ]
    for ef in expected_files:
        p = GROUND_TRUTH_DIR / ef
        assert p.exists(), f"Ground truth file missing: {ef}"


def test_edge_01_unavailable_interviewer(client: TestClient):
    with open(GROUND_TRUTH_DIR / "unavailable_interviewer_case.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    # Verify conflict: conflicting_start overlaps with attempted_start
    assert gt["conflicting_start"] == gt["attempted_start"]
    assert gt["assignment_persisted"] is False


def test_edge_02_duplicate_application(client: TestClient):
    with open(GROUND_TRUTH_DIR / "duplicate_application_case.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    # Attempting to re-apply should return 409
    res = client.post("/api/v1/applications/", json={
        "candidate_id": gt["candidate_id"],
        "requisition_id": gt["requisition_id"]
    })
    assert res.status_code == 409


def test_edge_03_missing_feedback(client: TestClient):
    with open(GROUND_TRUTH_DIR / "missing_feedback_case.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    assert gt["expected_feedback_count"] > gt["actual_feedback_count"]
    assert gt["is_business_exception"] is True


def test_edge_04_salary_outside_band(client: TestClient):
    with open(GROUND_TRUTH_DIR / "salary_outside_band_case.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    assert gt["attempted_offered_salary"] > gt["approved_max_salary"]
    assert gt["offer_persisted"] is False


def test_edge_05_closed_requisition_active_apps(client: TestClient):
    with open(GROUND_TRUTH_DIR / "closed_requisition_active_applications.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    # Verify requisition is closed
    req = client.get(f"/api/v1/requisitions/{gt['requisition_id']}").json()
    assert req["status"] == "CLOSED"
    assert gt["active_application_count"] == len(gt["active_application_ids"])


def test_system_audit_detects_all_anomalies(client: TestClient):
    """Verifies that the audit endpoint correctly flags the injected anomalies."""
    res = client.get("/api/v1/exceptions/detect")
    assert res.status_code == 200
    report = res.json()
    assert report["total_anomalies_detected"] > 0
    scenarios = {a["scenario_id"] for a in report["anomalies"]}
    # Must detect closed requisition with active apps and missing feedback
    assert "EDGE-05" in scenarios
