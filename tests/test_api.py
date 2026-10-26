from fastapi.testclient import TestClient

from talentgraph.api import app, _employees

client = TestClient(app)


def test_extract_skills_endpoint():
    response = client.post("/skills/extract", json={"text": "I know Python and SQL well."})
    assert response.status_code == 200
    skills = response.json()["skills"]
    assert "python" in skills
    assert "sql" in skills


def test_recommendations_endpoint_for_known_employee():
    employee_id = next(iter(_employees))
    response = client.get(f"/employees/{employee_id}/recommendations?top_k=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert "role_id" in body[0]
    assert "eligible" in body[0]


def test_recommendations_endpoint_404s_for_unknown_employee():
    response = client.get("/employees/E-9999/recommendations")
    assert response.status_code == 404


def test_fairness_report_endpoint():
    response = client.get("/fairness/report")
    assert response.status_code == 200
    body = response.json()
    assert "roles" in body
    assert "flagged_role_ids" in body
    assert len(body["roles"]) > 0
