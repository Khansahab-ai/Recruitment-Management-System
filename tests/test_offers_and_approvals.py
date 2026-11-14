from fastapi.testclient import TestClient


def test_salary_outside_approved_band_blocked(client: TestClient):
    # EDGE-04: Offer with salary exceeding max_salary must be rejected
    # Retrieve an application
    apps = client.get("/api/v1/applications/?status=INTERVIEW&limit=1").json()
    if not apps:
        apps = client.get("/api/v1/applications/?limit=1").json()
    app = apps[0]

    # Requisition max salary is typically <= 2,500,000. Try 100,000,000
    bad_offer = client.post("/api/v1/offers/", json={
        "application_id": app["application_id"],
        "offered_salary": 100000000.0
    })
    assert bad_offer.status_code == 422
    assert "outside the approved salary band" in bad_offer.json()["detail"]


def test_offer_approval_and_history(client: TestClient):
    offers = client.get("/api/v1/offers/?status=PENDING_APPROVAL&limit=1").json()
    if offers:
        target_offer = offers[0]
        off_id = target_offer["offer_id"]

        # Approve
        apprv = client.post(f"/api/v1/offers/{off_id}/approve", json={
            "decision": "APPROVED",
            "approver_id": 1,
            "comments": "Approved by VP of Engineering"
        })
        assert apprv.status_code == 200
        assert apprv.json()["status"] == "APPROVED"

        # Check approval history
        hist = client.get(f"/api/v1/offers/{off_id}/history")
        assert hist.status_code == 200
        events = hist.json()
        assert len(events) >= 1
        decisions = [e["decision"] for e in events]
        assert "APPROVED" in decisions
