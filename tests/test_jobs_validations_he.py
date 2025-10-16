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
def test_failure_on_empty_or_whitespace_title(client):
    r = client.post("/jobs/", json={"title": "   ", "company": "Acme"})
    assert r.status_code == 422
ddef test_failure_on_empty_company(client):
    r = client.post("/jobs/", json={"title": "Dev", "company": ""})
    assert r.status_code == 422
def test_failure_on_invalid_url(client):
    r = client.post("/jobs/", json={"title": "Dev", "company": "Acme", "url": "ftp://x"})
    assert r.status_code == 422
def test_failure_on_source_without_external_id(client):
    r = client.post("/jobs/", json={"title": "Dev", "company": "Acme", "source": "gh"})
    assert r.status_code == 422
def test_failure_on_external_id_without_source(client):
    r = client.post("/jobs/", json={"title": "Dev", "company": "Acme", "external_id": "1"})
    assert r.status_code == 422
def test_success_with_source_and_external_id_together(client):
    r = client.post("/jobs/", json={
        "title": "Dev",
        "company": "Acme",
        "source": "gh",
        "external_id": "1"
    })
    assert r.status_code == 200


