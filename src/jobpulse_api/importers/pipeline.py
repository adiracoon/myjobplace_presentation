"""Import pipeline with upsert logic"""
from typing import List, Dict
from datetime import datetime, timezone
import logging
from sqlmodel import Session
from sqlalchemy import text
from jobpulse_api.models import JobBase
logger = logging.getLogger(__name__)
class ImportPipeline:
    def __init__(self, session: Session):
        self.session = session
        self.stats = {"imported": 0, "updated": 0, "skipped": 0, "failed": 0}
    async def import_greenhouse_org(self, org: str) -> Dict:
        from jobpulse_api.importers.greenhouse import GreenhouseClient
        logger.info(f"Starting import for org: {org}")
        start_time = datetime.now(timezone.utc)
        try:
            client = GreenhouseClient(org)
            gh_jobs = await client.fetch_jobs()
            logger.info(f"Fetched {len(gh_jobs)} jobs from {org}")
            job_bases = [client.map_to_job_base(gh) for gh in gh_jobs]
            self._upsert_jobs(job_bases)
            self._save_checkpoint("greenhouse", org, start_time, "success")
            logger.info(f"Import complete: {self.stats}")
            return {"status": "success", "stats": self.stats}
        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            self._save_checkpoint("greenhouse", org, start_time, "failed")
            return {"status": "failed", "error": str(e), "stats": self.stats}
    def _upsert_jobs(self, jobs: List[JobBase]):
        """Upsert using column names for partial unique index"""
        upsert_sql = text("""
            INSERT INTO job (
                title, company, url, source, org, external_id,
                location, posted_at, updated_ext, is_active, is_demo, created_at
            ) VALUES (
                :title, :company, :url, :source, :org, :external_id,
                :location, :posted_at, :updated_ext, :is_active, :is_demo, :created_at
            )
            ON CONFLICT (source, external_id) WHERE source IS NOT NULL AND external_id IS NOT NULL
            DO UPDATE SET
                title = EXCLUDED.title,
                company = EXCLUDED.company,
                location = EXCLUDED.location,
                updated_ext = EXCLUDED.updated_ext
        """)
        for job_base in jobs:
            try:
                params = job_base.model_dump()
                params['created_at'] = datetime.now(timezone.utc)
                self.session.execute(upsert_sql, params)
                self.stats["updated"] += 1
            except Exception as e:
                logger.error(f"Failed job {job_base.external_id}: {e}")
                self.stats["failed"] += 1
                self.session.rollback()
                continue
        self.session.commit()
    def _save_checkpoint(self, source: str, org: str, start_time: datetime, status: str):
        checkpoint_sql = text("""
            INSERT INTO import_checkpoint (
                source, org, last_run_at, last_success_at,
                jobs_imported, jobs_updated, jobs_failed, status
            ) VALUES (
                :source, :org, :last_run_at, :last_success_at,
                :jobs_imported, :jobs_updated, :jobs_failed, :status
            )
            ON CONFLICT (source, org)
            DO UPDATE SET
                last_run_at = EXCLUDED.last_run_at,
                last_success_at = EXCLUDED.last_success_at,
                jobs_imported = EXCLUDED.jobs_imported,
                jobs_updated = EXCLUDED.jobs_updated,
                jobs_failed = EXCLUDED.jobs_failed,
                status = EXCLUDED.status
        """)
        self.session.execute(checkpoint_sql, {
            'source': source, 'org': org,
            'last_run_at': start_time,
            'last_success_at': datetime.now(timezone.utc) if status == "success" else start_time,
            'jobs_imported': self.stats["imported"],
            'jobs_updated': self.stats["updated"],
            'jobs_failed': self.stats["failed"],
            'status': status
        })
        self.session.commit()
