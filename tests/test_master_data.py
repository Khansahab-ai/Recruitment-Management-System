from fastapi.testclient import TestClient


def test_get_departments(client: TestClient):
    response = client.get("/api/v1/departments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    names = [d["name"] for d in data]
    assert "Engineering" in names
    assert "Data Science" in names


def test_get_job_requisitions(client: TestClient):
    response = client.get("/api/v1/requisitions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    first = data[0]
    assert "job_code" in first
    assert first["job_code"].startswith("REQ-2026-")
    assert first["min_salary"] <= first["max_salary"]


def test_get_candidates(client: TestClient):
    response = client.get("/api/v1/candidates/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    first = data[0]
    assert "candidate_code" in first
    assert first["candidate_code"].startswith("CAND-")


def test_get_skills(client: TestClient):
    response = client.get("/api/v1/skills/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 50


def test_get_resume_artifacts(client: TestClient):
    response = client.get("/api/v1/resumes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    first = data[0]
    assert "resume_id" in first
    assert first["file_type"] in ["PDF", "DOCX"]
