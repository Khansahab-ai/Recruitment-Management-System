from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient


def test_schedule_interview(client: TestClient):
    apps = client.get("/api/v1/applications/?status=SHORTLISTED&limit=1").json()
    if not apps:
        apps = client.get("/api/v1/applications/?limit=1").json()
    app_id = apps[0]["application_id"]

    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=1)

    res = client.post("/api/v1/interviews/", json={
        "application_id": app_id,
        "round_name": "Technical Round 1",
        "scheduled_start": start.isoformat(),
        "scheduled_end": end.isoformat()
    })
    assert res.status_code == 201
    data = res.json()
    assert data["interview_code"].startswith("INT-2026-")
    assert data["round_name"] == "Technical Round 1"


def test_interviewer_schedule_conflict_blocked(client: TestClient):
    # EDGE-01 scenario: Interviewer already booked for time slot cannot be double-booked
    import random
    days_offset = random.randint(200, 800)
    start = datetime.now(timezone.utc) + timedelta(days=days_offset)
    end = start + timedelta(hours=1)

    apps = client.get("/api/v1/applications/?limit=2").json()
    app_1 = apps[0]["application_id"]
    app_2 = apps[1]["application_id"]

    int_a = client.post("/api/v1/interviews/", json={
        "application_id": app_1,
        "round_name": "Conflict Round A",
        "scheduled_start": start.isoformat(),
        "scheduled_end": end.isoformat()
    }).json()

    int_b = client.post("/api/v1/interviews/", json={
        "application_id": app_2,
        "round_name": "Conflict Round B",
        "scheduled_start": start.isoformat(),
        "scheduled_end": end.isoformat()
    }).json()

    # Assign interviewer 1 to interview A
    assign_a = client.post(f"/api/v1/interviews/{int_a['interview_id']}/assign", json={
        "interviewer_id": 1
    })
    assert assign_a.status_code == 201

    # Attempt to assign the SAME interviewer 1 to interview B at the SAME time
    assign_b = client.post(f"/api/v1/interviews/{int_b['interview_id']}/assign", json={
        "interviewer_id": 1
    })
    assert assign_b.status_code == 409
    assert "Schedule conflict" in assign_b.json()["detail"]
