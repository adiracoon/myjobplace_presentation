"""Greenhouse API client and mapper"""
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import httpx
from jobpulse_api.models import JobBase
from jobpulse_api.importers.rate_limiter import RateLimiter
class GreenhouseLocation(BaseModel):
    name: str
class GreenhouseDepartment(BaseModel):
    id: int
    name: str
class GreenhouseJob(BaseModel):
    """Single job from Greenhouse API"""
    id: int
    title: str
    updated_at: datetime
    location: GreenhouseLocation
    absolute_url: str
    departments: List[GreenhouseDepartment] = Field(default_factory=list)
class GreenhouseResponse(BaseModel):
    """Full API response"""
    jobs: List[GreenhouseJob]
class GreenhouseClient:
    """Fetch jobs from Greenhouse API"""
    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{org}/jobs"
    def __init__(self, org: str, rate_limit: float = 5.0):
        self.org = org
        self.limiter = RateLimiter(rate=rate_limit, burst=10)
    async def fetch_jobs(self) -> List[GreenhouseJob]:
        """Fetch all jobs for this org"""
        url = self.BASE_URL.format(org=self.org)
        async with httpx.AsyncClient(timeout=30.0) as client:
            await self.limiter.acquire()
            response = await client.get(url)
            response.raise_for_status()
            data = GreenhouseResponse.model_validate(response.json())
            return data.jobs
    def map_to_job_base(self, gh_job: GreenhouseJob) -> JobBase:
        """Convert Greenhouse job to our JobBase model"""
        updated_utc = gh_job.updated_at
        if updated_utc.tzinfo is not None:
            updated_utc = updated_utc.astimezone(timezone.utc)
        return JobBase(
            title=gh_job.title,
            company=self.org.replace("-", " ").title(),  # "stripe" → "Stripe"
            url=gh_job.absolute_url,
            source="greenhouse",
            org=self.org,
            external_id=str(gh_job.id),
            location=gh_job.location.name if gh_job.location else None,
            posted_at=None,  # Greenhouse doesn't provide this
            updated_ext=updated_utc,
            is_active=True,
            is_demo=False
        )
