"""Tests for PUT /jobs/{id} — partial updates, 404 when not found, and 409 on duplication."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    SQLModel.metadata.create_all(engine)
    def _override():
        with Session(engine) as s:
            yield s
    app = create_app()
    app.dependency_overrides[get_session] = _override
    return TestClient(app)
def seed(client):
    a = {"title": "A", "company": "C1", "source": "gh", "external_id": "1", "location": "TLV"}
    b = {"title": "B", "company": "C2", "source": "gh", "external_id": "2", "location": "JLM"}
    r1 = client.post("/jobs/", json=a).json()
    r2 = client.post("/jobs/", json=b).json()
    return r1["id"], r2["id"]
def test_partial_update_succeeds(client):
    jid1, _ = seed(client)
    r = client.put(f"/jobs/{jid1}", json={"location": "Remote"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["location"] == "Remote", "location field should be updated"
    assert body["title"] == "A" and body["company"] == "C1", "fields not sent should remain unchanged"
def test_404_when_record_missing(client):
    r = client.put("/jobs/999999", json={"location": "Nowhere"})
    assert r.status_code == 404
def test_409_when_update_creates_duplicate(client):
    jid1, jid2 = seed(client)
    dup = client.put(f"/jobs/{jid2}", json={"external_id": "1"})
    assert dup.status_code == 409, dup.text
    assert "Conflict" in dup.json()["detail"]
def test_update_multiple_fields_without_duplication(client):
    jid1, _ = seed(client)
    r = client.put(f"/jobs/{jid1}", json={"title": "A2", "company": "C1", "is_active": False})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "A2" and body["is_active"] is False






