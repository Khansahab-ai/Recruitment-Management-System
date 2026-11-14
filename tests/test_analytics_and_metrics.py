from fastapi.testclient import TestClient


def test_recruitment_funnel_metrics(client: TestClient):
    res = client.get("/api/v1/analytics/funnel")
    assert res.status_code == 200
    data = res.json()
    assert data["total_applications"] >= 3000
    stages = [s["stage"] for s in data["funnel"]]
    assert "APPLIED" in stages
    assert "SCREENED" in stages
    assert "SHORTLISTED" in stages
    assert "INTERVIEWED" in stages
    assert "OFFERED" in stages
    assert "ACCEPTED" in stages


def test_operational_kpis(client: TestClient):
    res = client.get("/api/v1/analytics/kpis")
    assert res.status_code == 200
    kpis = res.json()
    assert kpis["total_requisitions"] >= 100
    assert kpis["total_candidates"] >= 2000
    assert kpis["total_applications"] >= 3000
    assert kpis["total_interviews"] >= 600
    assert kpis["total_offers"] >= 150
    assert 0.0 <= kpis["offer_acceptance_rate_percent"] <= 100.0
    assert kpis["avg_time_to_hire_days"] > 0


def test_department_performance(client: TestClient):
    res = client.get("/api/v1/analytics/departments")
    assert res.status_code == 200
    depts = res.json()
    assert len(depts) >= 10
    total_reqs = sum(d["total_requisitions"] for d in depts)
    assert total_reqs >= 100
