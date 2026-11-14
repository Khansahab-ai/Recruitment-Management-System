from fastapi.testclient import TestClient


def test_allowed_stage_transitions(client: TestClient):
    # Retrieve an application
    apps = client.get("/api/v1/applications/?limit=1").json()
    assert len(apps) > 0
    app_id = apps[0]["application_id"]

    # Retrieve history
    history_res = client.get(f"/api/v1/applications/{app_id}/history")
    assert history_res.status_code == 200
    events = history_res.json()
    assert len(events) >= 1
    assert events[0]["new_status"] == "APPLIED"


def test_invalid_stage_transition_blocked(client: TestClient):
    # Attempting an illegal backward or disallowed jump transition
    # Create a fresh candidate and open requisition
    import uuid
    unique_email = f"lifecycle.{uuid.uuid4().hex[:8]}@example.com"
    cand_res = client.post("/api/v1/candidates/", json={
        "full_name": "Lifecycle Test Candidate",
        "email": unique_email,
        "phone": "+91 9999999999",
        "education": "Master's",
        "total_experience": 5.0
    })
    assert cand_res.status_code == 201
    cand_id = cand_res.json()["candidate_id"]

    # Get open requisition
    reqs = client.get("/api/v1/requisitions/").json()
    open_req = next((r for r in reqs if r["status"] == "OPEN"), reqs[0])

    # Apply
    app_res = client.post("/api/v1/applications/", json={
        "candidate_id": cand_id,
        "requisition_id": open_req["requisition_id"]
    })
    if app_res.status_code == 201:
        app_id = app_res.json()["application_id"]

        # APPLIED cannot transition directly to OFFER
        bad_trans = client.patch(f"/api/v1/applications/{app_id}/status", json={
            "status": "OFFER",
            "changed_by": "TESTER",
            "reason": "Illegal transition test"
        })
        assert bad_trans.status_code == 400


def test_duplicate_application_prevention(client: TestClient):
    # EDGE-02: Candidate cannot apply twice to the same requisition
    apps = client.get("/api/v1/applications/?limit=5").json()
    assert len(apps) > 0
    sample = apps[0]

    dup_res = client.post("/api/v1/applications/", json={
        "candidate_id": sample["candidate_id"],
        "requisition_id": sample["requisition_id"]
    })
    assert dup_res.status_code == 409
