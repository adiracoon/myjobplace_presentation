"""Supplementary tests: API contract, pagination/filtering/booleans, create/update, DB isolation, and DB file creation."""
import json, os, pathlib, re
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
@pytest.fixture()
def client_mem():
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
def test_root_contract(client_mem):
    r = client_mem.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("message") == "JobPulse API" and "/docs" in body.get("docs", "/docs")
def test_openapi_has_paths(client_mem):
    r = client_mem.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    for p in ("/health", "/readyz", "/jobs/", "/jobs/count", "/jobs/{job_id}"):
        assert p in paths, f"Path {p} must appear in OpenAPI contract"
def test_list_pagination_and_filters(client_mem):
    for payload in [
        {"title":"A","company":"Acme","source":"gh","external_id":"1","is_active":True},
        {"title":"B","company":"Acme","source":"gh","external_id":"2","is_active":False},
        {"title":"C","company":"Globex","source":"lever","external_id":"3","is_active":True},
    ]:
        assert client_mem.post("/jobs/", json=payload).status_code == 200
    assert client_mem.get("/jobs/?limit=2").status_code == 200
    assert len(client_mem.get("/jobs/?limit=2").json()) == 2
    acme = client_mem.get("/jobs/?company=Acme").json()
    assert len(acme) == 2
    active = client_mem.get("/jobs/?is_active=true").json()
    assert all(row["is_active"] for row in active)
def test_limit_bounds_validation(client_mem):
    assert client_mem.get("/jobs/?limit=0").status_code == 422
    assert client_mem.get("/jobs/?limit=101").status_code == 422
    assert client_mem.get("/jobs/?skip=-1").status_code == 422
def test_create_and_conflict_409(client_mem):
    ok = {"title":"Dev","company":"X","source":"gh","external_id":"42"}
    assert client_mem.post("/jobs/", json=ok).status_code == 200
    dup = {"title":"Dev2","company":"Y","source":"gh","external_id":"42"}
    r = client_mem.post("/jobs/", json=dup)
    assert r.status_code == 409 and "Conflict" in r.json()["detail"]
def test_put_partial_404_409(client_mem):
    assert client_mem.put("/jobs/999999", json={"title":"Nope"}).status_code == 404
    j1 = client_mem.post("/jobs/", json={"title":"A","company":"C","source":"gh","external_id":"1"}).json()
    j2 = client_mem.post("/jobs/", json={"title":"B","company":"C","source":"gh","external_id":"2"}).json()
    r = client_mem.put(f"/jobs/{j2['id']}", json={"external_id":"1"})
    assert r.status_code == 409
    ok = client_mem.put(f"/jobs/{j1['id']}", json={"location":"Remote","is_active":False})
    assert ok.status_code == 200 and ok.json()["location"] == "Remote" and ok.json()["is_active"] is False
def test_count_filters(client_mem):
    client_mem.post("/jobs/", json={"title":"A","company":"Acme","source":"gh","external_id":"1","is_active":True})
    client_mem.post("/jobs/", json={"title":"B","company":"Acme","source":"gh","external_id":"2","is_active":False})
    client_mem.post("/jobs/", json={"title":"C","company":"Globex","source":"lever","external_id":"3","is_active":True})
    assert client_mem.get("/jobs/count").json()["count"] == 3
    assert client_mem.get("/jobs/count?company=Acme").json()["count"] == 2
    assert client_mem.get("/jobs/count?source=lever&is_active=true").json()["count"] == 1
def test_startup_creates_db_file_isolated(tmp_path, monkeypatch):
    dbfile = tmp_path / "jobpulse_local.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{dbfile}")
    app = create_app()
    with TestClient(app) as c:
        assert c.get("/health").status_code == 200
    assert dbfile.exists(), "init_db should create the SQLite file"
