from typing import List, Optional
from datetime import datetime, timezone
import os
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi.security import APIKeyHeader
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, Session
from jobpulse_api.db import get_session
from jobpulse_api.models import Job, JobBase, JobRead, JobUpdate
router = APIRouter(prefix="/jobs", tags=["jobs"])
API_KEYS = {k.strip() for k in os.getenv("JOBPULSE_API_KEYS", "").split(",") if k.strip()}
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """Require API key for write operations (if configured)"""
    if not API_KEYS:
        return "anonymous"  # Dev mode: no auth required
    if api_key and api_key in API_KEYS:
        return api_key
    raise HTTPException(status_code=401, detail="Invalid or missing API key")
@router.get("/", response_model=List[JobRead])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
    source: Optional[str] = None,
    company: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    session: Session = Depends(get_session),
):
    """List jobs with pagination and filters"""
    stmt = select(Job).offset(skip).limit(limit)
    if not include_deleted:
        stmt = stmt.where(Job.deleted_at.is_(None))
    if source is not None:
        stmt = stmt.where(Job.source == source)
    if company is not None:
        stmt = stmt.where(Job.company == company)
    if is_active is not None:
        stmt = stmt.where(Job.is_active == is_active)
    return session.exec(stmt).all()
@router.get("/count")
def count_jobs(
    source: Optional[str] = None,
    company: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    session: Session = Depends(get_session),
):
    """Count jobs with filters"""
    stmt = select(func.count()).select_from(Job)
    if not include_deleted:
        stmt = stmt.where(Job.deleted_at.is_(None))
    if source is not None:
        stmt = stmt.where(Job.source == source)
    if company is not None:
        stmt = stmt.where(Job.company == company)
    if is_active is not None:
        stmt = stmt.where(Job.is_active == is_active)
    total = session.exec(stmt).one()
    return {"count": int(total)}
@router.post("/", response_model=JobRead, status_code=200)
def create_job(
    job: JobBase,
    session: Session = Depends(get_session),
    _api_key: str = Depends(require_api_key),
):
    """Create a new job (with 409 on duplicate source+external_id)"""
    if job.source and job.external_id:
        exists = session.exec(
            select(Job).where(
                (Job.source == job.source) & 
                (Job.external_id == job.external_id)
            )
        ).first()
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Conflict: job with the same (source, external_id) already exists"
            )
    try:
        obj = Job.model_validate(job)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflict: unique constraint violation (source, external_id)"
        )
@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    job: JobUpdate,
    session: Session = Depends(get_session),
    _api_key: str = Depends(require_api_key),
):
    """Update job partially (with 409 on conflict)"""
    obj = session.get(Job, job_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Job not found")
    data = job.model_dump(exclude_unset=True)
    new_source = data.get("source", obj.source)
    new_external = data.get("external_id", obj.external_id)
    if new_source and new_external:
        exists = session.exec(
            select(Job).where(
                (Job.source == new_source) &
                (Job.external_id == new_external) &
                (Job.id != job_id)
            )
        ).first()
        if exists:
            raise HTTPException(
                status_code=409,
                detail="Conflict: another job already has this (source, external_id)"
            )
    for k, v in data.items():
        setattr(obj, k, v)
    try:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conflict: unique constraint violation (source, external_id)"
        )
@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    session: Session = Depends(get_session),
    _api_key: str = Depends(require_api_key),
):
    """Soft delete a job (idempotent)"""
    obj = session.get(Job, job_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Job not found")
    if obj.deleted_at is not None:
        return {
            "id": job_id,
            "deleted": True,
            "deleted_at": obj.deleted_at.isoformat(),
            "already_deleted": True
        }
    obj.deleted_at = datetime.now(timezone.utc)
    obj.is_active = False
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return {
        "id": job_id,
        "deleted": True,
        "deleted_at": obj.deleted_at.isoformat()
    }
