from fastapi.testclient import TestClient


def test_screening_rule_retrieval(client: TestClient):
    res = client.get("/api/v1/screening/rules?requisition_id=1")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 1
    total_weight = sum(r["weight"] for r in rules)
    assert total_weight == 100.0


def test_screening_rule_weight_cap(client: TestClient):
    # Attempting to add a rule that exceeds 100% total weight
    bad_rule = client.post("/api/v1/screening/rules", json={
        "requisition_id": 1,
        "criteria_name": "EXCESS_WEIGHT_TEST",
        "weight": 50.0,
        "minimum_score": 60.0,
        "is_mandatory": False
    })
    assert bad_rule.status_code == 422


def test_application_screening_evaluation(client: TestClient):
    apps = client.get("/api/v1/applications/?limit=10").json()
    app_id = apps[0]["application_id"]

    eval_res = client.post(f"/api/v1/screening/evaluate/{app_id}")
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert "total_score" in data
    assert 0.0 <= data["total_score"] <= 100.0
    assert "is_qualified" in data
    assert data["recommended_stage"] in ["SHORTLISTED", "REJECTED"]
