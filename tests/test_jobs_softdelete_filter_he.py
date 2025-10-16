import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
@pytest.fixture()
def client(monkeypatch):
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
def test_default_excludes_deleted_and_include_deleted_returns_them(client):
    a = client.post("/jobs/", json={"title": "A", "company": "X"}).json()
    b = client.post("/jobs/", json={"title": "B", "company": "Y"}).json()
    client.delete(f"/jobs/{a['id']}")
    lst = client.get("/jobs/").json()
    assert [j["id"] for j in lst] == [b["id"]]
    assert client.get("/jobs/count").json()["count"] == 1
    lst2 = client.get("/jobs/?include_deleted=true").json()
    ids = sorted([j["id"] for j in lst2])
    assert ids == sorted([a["id"], b["id"]])
    assert client.get("/jobs/count?include_deleted=true").json()["count"] == 2
