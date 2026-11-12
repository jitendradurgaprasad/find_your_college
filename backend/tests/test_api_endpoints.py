import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "OPERATIONAL"
    assert "Find Your Collage" in data["platform"]

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

def test_list_universities():
    resp = client.get("/api/universities")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["total"] >= 1
    names = [u["name"] for u in data["results"]]
    short_names = [u.get("short_name") or "" for u in data["results"]]
    all_names = " ".join(names + short_names)
    assert any(keyword in all_names for keyword in ["Bombay", "Hyderabad", "Pilani", "IIT", "BITS"])

def test_get_university_profile():
    # First get list
    list_resp = client.get("/api/universities")
    first_id = list_resp.json()["results"][0]["id"]

    prof_resp = client.get(f"/api/universities/{first_id}")
    assert prof_resp.status_code == 200
    data = prof_resp.json()
    assert data["id"] == first_id
    assert "programs" in data
    assert "admissions" in data
    assert "scholarships" in data
    assert "placements" in data
    assert "traceable_facts" in data

def test_data_quality_endpoint():
    resp = client.get("/api/data-quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_institutions"] >= 1
    assert "verified_records" in data
    assert "category_breakdown" in data

def test_college_comparison():
    list_resp = client.get("/api/universities")
    results = list_resp.json()["results"]
    if len(results) >= 2:
        id1 = results[0]["id"]
        id2 = results[1]["id"]
        cmp_resp = client.post("/api/universities/compare", json={"university_ids": [id1, id2]})
        assert cmp_resp.status_code == 200
        cmp_data = cmp_resp.json()
        assert len(cmp_data["colleges"]) == 2
        assert "location" in cmp_data["colleges"][0]
        assert "admission_status" in cmp_data["colleges"][0]

def test_monitoring_endpoint():
    resp = client.get("/api/monitoring/changes")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_crawl_validation():
    # Attempting to crawl localhost or SSRF target should fail with 400
    resp = client.post("/api/crawl/start", json={"url": "http://127.0.0.1:8000/secret"})
    assert resp.status_code == 400
    assert "SSRF" in resp.json()["detail"] or "Private" in resp.json()["detail"]
