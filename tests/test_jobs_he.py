"""Functional tests for job listing and counting — without writing to disk (in-memory)."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
from jobpulse_api.models import Job
@pytest.fixture()
def client():
    """Creates an app with an in-memory-only DB — fast tests with no side effects."""
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
def test_empty_list_and_zero_count(client):
    assert client.get("/jobs/").json() == [], "The list should initially be empty"
    assert client.get("/jobs/count").json() == {"count": 0}, "Initial count should be 0"
@pytest.mark.parametrize("limit,test_coloring", [(0, "limit=0"), (101, "limit=101")])
def test_validation_limit(client, limit, test_coloring):
    assert client.get(f"/jobs/?limit={limit}").status_code == 422, f"Invalid limit ({test_coloring}) should be rejected"
@pytest.mark.parametrize("skip", [-1])
def test_validation_skip(client, skip):
    assert client.get(f"/jobs/?skip={skip}").status_code == 422, "Negative skip should be rejected"
def test_filter_count_and_result_order(client):
    with client.app.dependency_overrides[get_session]().__next__() as s:  # type: ignore
        s.add(Job(title="BE", company="Acme", source="gh", external_id="1", is_active=True))
        s.add(Job(title="BE", company="Acme", source="gh", external_id="2", is_active=False))
        s.add(Job(title="FE", company="Globex", source="lever", external_id="3", is_active=True))
        s.commit()
    assert client.get("/jobs/count").json()["count"] == 3, "Invalid overall count"
    ids = [row["id"] for row in client.get("/jobs/").json()]
    assert ids == sorted(ids), "Results should be sorted by id"
    assert client.get("/jobs/count?source=gh").json()["count"] == 2, "Filtering by source failed"
    assert client.get("/jobs/count?company=Acme").json()["count"] == 2, "Filtering by company failed"
    assert client.get("/jobs/count?is_active=true").json()["count"] == 2, "Filtering by is_active failed"
    rows = client.get("/jobs/?source=gh&company=Acme&is_active=true").json()
    assert len(rows) == 1 and rows[0]["company"] == "Acme", "Combining filters should return a single row for Acme"
def test_simple_pagination(client):
    with client.app.dependency_overrides[get_session]().__next__() as s:  # type: ignore
        for i in range(5):
            s.add(Job(title=f"T{i}", company="A", source="S", external_id=str(i)))
        s.commit()
    assert len(client.get("/jobs/?limit=2").json()) == 2, "limit=2 should restrict to two results"
    assert len(client.get("/jobs/?skip=4").json()) <= 1, "skip=4 should skip almost all results"
