"""Tests for POST /jobs — valid creation, validation, and duplicates (409)."""
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
def test_minimal_creation_succeeds(client):
    payload = {"title": "Backend Dev", "company": "Acme"}
    r = client.post("/jobs/", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] > 0 and body["company"] == "Acme"
    assert body["is_active"] is True and body["is_demo"] is False
    assert client.get("/jobs/count").json()["count"] == 1
@pytest.mark.parametrize("bad", [
    {"company": "Acme"},           # missing title
    {"title": "Backend Dev"},      # missing company
])
def test_missing_fields_validation_returns_422(client, bad):
    assert client.post("/jobs/", json=bad).status_code == 422
def test_duplicates_409_by_source_external_id(client):
    ok1 = {"title": "BE", "company": "Acme", "source": "gh", "external_id": "1"}
    ok2 = {"title": "BE2", "company": "Acme", "source": "gh", "external_id": "2"}
    dup = {"title": "BE3", "company": "Acme", "source": "gh", "external_id": "1"}
    assert client.post("/jobs/", json=ok1).status_code == 200
    assert client.post("/jobs/", json=ok2).status_code == 200
    r = client.post("/jobs/", json=dup)
    assert r.status_code == 409, r.text
    assert "Conflict" in r.json()["detail"]
def test_duplicates_allowed_without_source_and_external_id(client):
    """When source/external_id are missing, similar jobs are allowed (no unique constraint)."""
    a = {"title": "Dev", "company": "X"}
    b = {"title": "Dev", "company": "X"}
    assert client.post("/jobs/", json=a).status_code == 200
    assert client.post("/jobs/", json=b).status_code == 200
