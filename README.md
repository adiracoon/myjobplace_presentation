**Live:** [https://app.myjobplace.app](https://app.myjobplace.app)
<p align="center">
  <img src="docs/screenshot.png" alt="JobPulse Interface" width="800" />
</p>
Generic job boards create a noisy firehose. I wanted a precise, low-noise feed so candidates spend less time sifting.
An MVP that aggregates public company career pages and ATS sources (e.g., Greenhouse, Lever) into one API with a simple Hebrew UI for fast filtering by title, company, and location.
- **Backend:** FastAPI, SQLModel, Alembic
- **Frontend:** Vanilla JavaScript (static assets)
- **Database:** SQLite/PostgreSQL
```
GET  /health        - Health check
GET  /readyz        - Readiness check
GET  /jobs          - List all jobs (with filters)
GET  /jobs/count    - Total job count
```
- Global dataset with Israel-only focus planned
- Browse and filter jobs
- No user accounts, alerts, or apply flows yet
- Add Israel-focused sources and manual curation
- Stronger deduplication and normalization across sources
- Saved filters and lightweight alerts (optional)
```bash
pip install -r requirements.txt
uvicorn jobpulse_api.main:app --app-dir src --host 127.0.0.1 --port 8010
```
---
**Note:** This is an MVP focused on solving the job search noise problem for the Israeli market.
