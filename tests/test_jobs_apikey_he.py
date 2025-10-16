import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("JOBPULSE_API_KEYS", "devkey")
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
def test_write_without_key_is_blocked(client):
    import jobpulse_api.routes.jobs as jobs_module
    original_keys = jobs_module.API_KEYS
    jobs_module.API_KEYS = {"devkey"}  # enforcement
    try:
        r = client.post("/jobs/", json={"title": "Dev", "company": "Acme"})
        assert r.status_code == 401
    finally:
        jobs_module.API_KEYS = original_keys
def test_write_with_key_succeeds(client):
    import jobpulse_api.routes.jobs as jobs_module
    original_keys = jobs_module.API_KEYS
    jobs_module.API_KEYS = {"devkey"}
    try:
        r = client.post("/jobs/", headers={"X-API-Key": "devkey"}, json={"title": "Dev", "company": "Acme"})
        assert r.status_code == 200
        jid = r.json()["id"]
        r2 = client.delete(f"/jobs/{jid}", headers={"X-API-Key": "devkey"})
        assert r2.status_code == 200
    finally:
        jobs_module.API_KEYS = original_keys






