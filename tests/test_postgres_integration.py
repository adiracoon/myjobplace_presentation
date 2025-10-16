"""Integration tests with real Postgres"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, select, text
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from jobpulse_api.main import create_app
from jobpulse_api.db import get_session
from jobpulse_api.models import Job, ImportCheckpoint
PG_URL = os.getenv("DATABASE_URL")
@pytest.fixture(scope="function")
def pg_session():
    """Session with real Postgres, cleanup before/after"""
    if not PG_URL or not PG_URL.startswith("postgresql"):
        pytest.skip("DATABASE_URL not set or not postgres")
    engine = create_engine(PG_URL, echo=False)
    with Session(engine) as s:
        s.exec(text("TRUNCATE TABLE job, import_checkpoint RESTART IDENTITY CASCADE"))
        s.commit()
    yield engine
    with Session(engine) as s:
        s.exec(text("TRUNCATE TABLE job, import_checkpoint RESTART IDENTITY CASCADE"))
        s.commit()
@pytest.fixture()
def pg_client(pg_session):
    """TestClient with Postgres backend"""
    app = create_app()
    def _override():
        with Session(pg_session) as s:
            yield s
    app.dependency_overrides[get_session] = _override
    return TestClient(app)
def test_schema_and_indexes_exist(pg_session):
    """Verify schema and indexes exist"""
    inspector = inspect(pg_session)
    tables = inspector.get_table_names()
    assert 'job' in tables, "job table missing"
    assert 'import_checkpoint' in tables, "import_checkpoint missing"
    indexes = inspector.get_indexes('job')
    index_names = {idx['name'] for idx in indexes}
    assert 'ix_job_posted_at' in index_names
    assert 'ix_job_company_title' in index_names
    assert 'uq_job_source_external' in index_names
    print(f"✓ Found {len(indexes)} indexes on job table")
def test_full_crud_with_soft_delete(pg_client):
    """Full CRUD including soft delete"""
    r = pg_client.post("/jobs/", json={
        "title": "Backend Engineer",
        "company": "TestCorp",
        "source": "gh",
        "external_id": "test-001",
        "location": "Tel Aviv"
    })
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]
    jobs = pg_client.get("/jobs/").json()
    assert len(jobs) == 1
    assert jobs[0]["id"] == job_id
    r = pg_client.put(f"/jobs/{job_id}", json={"location": "Remote"})
    assert r.status_code == 200
    assert r.json()["location"] == "Remote"
    r = pg_client.delete(f"/jobs/{job_id}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True
    jobs = pg_client.get("/jobs/").json()
    assert len(jobs) == 0, "Deleted job should be excluded"
    jobs_all = pg_client.get("/jobs/?include_deleted=true").json()
    assert len(jobs_all) == 1
    assert jobs_all[0]["deleted_at"] is not None
def test_unique_constraint_at_db_level(pg_session):
    """Verify DB-level unique constraint works"""
    with Session(pg_session) as s:
        j1 = Job(
            title="Job1",
            company="Company",
            source="gh",
            external_id="same-id",
            is_active=True
        )
        s.add(j1)
        s.commit()
        j2 = Job(
            title="Job2",
            company="Company",
            source="gh",
            external_id="same-id",
            is_active=True
        )
        s.add(j2)
        with pytest.raises(IntegrityError) as exc:
            s.commit()
        assert "uq_job_source_external" in str(exc.value).lower()
def test_null_source_external_id_allows_duplicates(pg_client):
    """Verify duplicates allowed when source/external_id are NULL"""
    r1 = pg_client.post("/jobs/", json={"title": "Job1", "company": "Co"})
    r2 = pg_client.post("/jobs/", json={"title": "Job2", "company": "Co"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    count = pg_client.get("/jobs/count").json()["count"]
    assert count == 2, "Should allow NULL duplicates"
def test_409_on_duplicate_via_api(pg_client):
    """Verify API returns 409 on duplicates"""
    payload = {
        "title": "Dev",
        "company": "Corp",
        "source": "gh",
        "external_id": "unique-123"
    }
    r1 = pg_client.post("/jobs/", json=payload)
    assert r1.status_code == 200
    r2 = pg_client.post("/jobs/", json=payload)
    assert r2.status_code == 409
    assert "conflict" in r2.json()["detail"].lower()
def test_pagination_and_filters(pg_client):
    """Verify pagination and filtering"""
    for i in range(5):
        pg_client.post("/jobs/", json={
            "title": f"Job{i}",
            "company": "Acme" if i < 3 else "Globex",
            "source": "gh",
            "external_id": f"id-{i}"
        })
    jobs = pg_client.get("/jobs/?limit=2").json()
    assert len(jobs) == 2
    acme_jobs = pg_client.get("/jobs/?company=Acme").json()
    assert len(acme_jobs) == 3
    count = pg_client.get("/jobs/count?company=Globex").json()["count"]
    assert count == 2
def test_import_checkpoint_crud(pg_session):
    """Verify ImportCheckpoint works"""
    from datetime import datetime, timezone
    with Session(pg_session) as s:
        cp = ImportCheckpoint(
            source="greenhouse",
            org="airbnb",
            last_run_at=datetime.now(timezone.utc),
            last_success_at=datetime.now(timezone.utc),
            jobs_imported=100,
            jobs_updated=10,
            jobs_failed=2,
            status="success"
        )
        s.add(cp)
        s.commit()
        result = s.exec(
            select(ImportCheckpoint).where(
                ImportCheckpoint.source == "greenhouse",
                ImportCheckpoint.org == "airbnb"
            )
        ).first()
        assert result is not None
        assert result.jobs_imported == 100
        assert result.status == "success"
def test_stress_unique_constraint(pg_session):
    """Stress test - inserting multiple duplicates"""
    with Session(pg_session) as s:
        j1 = Job(
            title="Original",
            company="Co",
            source="lever",
            external_id="stress-1",
            is_active=True
        )
        s.add(j1)
        s.commit()
        failures = 0
        for i in range(10):
            try:
                dup = Job(
                    title=f"Dup{i}",
                    company="Co",
                    source="lever",
                    external_id="stress-1",
                    is_active=True
                )
                s.add(dup)
                s.commit()
            except IntegrityError:
                s.rollback()
                failures += 1
        assert failures == 10, f"Expected 10 failures, got {failures}"
        count = s.exec(select(Job)).all()
        assert len(count) == 1
