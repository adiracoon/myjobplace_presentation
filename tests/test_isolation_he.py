"""Isolation test: overriding the session does not modify the default SQLite file."""
import os, time
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
import jobpulse_api.db as db
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobpulse_dev.sqlite")
@pytest.fixture()
def baseline_db_file():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        open(DB_FILE, "a").close()
    return os.stat(DB_FILE).st_mtime
def test_override_does_not_modify_db_file(baseline_db_file, monkeypatch):
    """Disable init_db to avoid touching the default, and use an in-memory DB only."""
    monkeypatch.setattr(db, "init_db", lambda: None)
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
    client = TestClient(app)
    assert client.get("/jobs/").status_code == 200
    assert client.get("/jobs/count").status_code == 200
    after = os.stat(DB_FILE).st_mtime
    assert after == baseline_db_file, "Using the override should not modify the default DB file"
