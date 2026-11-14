from fastapi.testclient import TestClient


def test_submit_valid_feedback(client: TestClient):
    # Find an interview and an assigned interviewer
    intvs = client.get("/api/v1/interviews/?limit=5").json()
    target_intv = None
    target_ivr_id = None

    for i in intvs:
        if i["assignments"]:
            target_intv = i
            target_ivr_id = i["assignments"][0]["interviewer_id"]
            break

    if target_intv:
        # Check if feedback already exists or submit
        fb_res = client.post("/api/v1/feedback/", json={
            "interview_id": target_intv["interview_id"],
            "interviewer_id": target_ivr_id,
            "technical_score": 8.5,
            "problem_solving_score": 9.0,
            "communication_score": 7.5,
            "recommendation": "HIRE",
            "comments": "Strong technical skills demonstrated."
        })
        # If already exists, expect 409, else 201
        assert fb_res.status_code in [201, 409]


def test_unassigned_interviewer_feedback_blocked(client: TestClient):
    # An interviewer not on the panel cannot submit feedback
    intvs = client.get("/api/v1/interviews/?limit=1").json()
    intv = intvs[0]

    # Use an invalid / non-assigned interviewer id (e.g. 99999 or unassigned)
    bad_res = client.post("/api/v1/feedback/", json={
        "interview_id": intv["interview_id"],
        "interviewer_id": 99999,
        "technical_score": 5.0,
        "problem_solving_score": 5.0,
        "communication_score": 5.0,
        "recommendation": "NO_HIRE",
        "comments": "Test"
    })
    assert bad_res.status_code in [400, 404]


def test_feedback_completeness_check(client: TestClient):
    intvs = client.get("/api/v1/interviews/?limit=10").json()
    for intv in intvs:
        chk = client.get(f"/api/v1/feedback/completeness/{intv['interview_id']}")
        assert chk.status_code == 200
        data = chk.json()
        assert "is_complete" in data
        assert "expected_feedback_count" in data
        assert "submitted_feedback_count" in data
        break
