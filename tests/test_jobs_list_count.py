import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
from jobpulse_api.models import Job
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
def test_list_empty_and_count_zero(client):
    r = client.get("/jobs/")
    assert r.status_code == 200 and r.json() == []
    r = client.get("/jobs/count")
    assert r.status_code == 200 and r.json() == {"count": 0}
def test_pagination_validation(client):
    assert client.get("/jobs/?limit=0").status_code == 422
    assert client.get("/jobs/?limit=101").status_code == 422
    assert client.get("/jobs/?skip=-1").status_code == 422
def test_filters_and_count(client):
    with client.app.dependency_overrides[get_session]().__next__() as s:  # type: ignore
        s.add(Job(title="BE", company="Acme", source="gh", external_id="1", is_active=True))
        s.add(Job(title="BE", company="Acme", source="gh", external_id="2", is_active=False))
        s.add(Job(title="FE", company="Globex", source="lever", external_id="3", is_active=True))
        s.commit()
    assert client.get("/jobs/count").json()["count"] == 3
    assert len(client.get("/jobs/").json()) == 3
    assert client.get("/jobs/count?source=gh").json()["count"] == 2
    assert len(client.get("/jobs/?source=gh").json()) == 2
    assert client.get("/jobs/count?company=Acme").json()["count"] == 2
    assert len(client.get("/jobs/?company=Acme").json()) == 2
    assert client.get("/jobs/count?is_active=true").json()["count"] == 2
    assert len(client.get("/jobs/?is_active=true").json()) == 2
    assert client.get("/jobs/count?source=gh&company=Acme&is_active=true").json()["count"] == 1
    rows = client.get("/jobs/?source=gh&company=Acme&is_active=true").json()
    assert len(rows) == 1 and rows[0]["company"] == "Acme"
