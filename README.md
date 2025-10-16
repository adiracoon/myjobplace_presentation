**Live:** [https://app.myjobplace.app](https://app.myjobplace.app)
<p align="center">
  <img src="docs/screenshot.png" alt="JobPulse" width="600" />
</p>
Generic job boards create a noisy firehose. I wanted a precise, low-noise feed so candidates spend less time sifting.
An MVP that aggregates public company career pages and ATS sources (e.g., Greenhouse, Lever) into one API with a simple Hebrew UI for fast filtering by title, company, and location.
- **Backend:** FastAPI, SQLModel, Alembic
- **Frontend:** Vanilla JavaScript
- **Database:** SQLite/PostgreSQL
```
GET  /health        Health check
GET  /readyz        Readiness check
GET  /jobs          List jobs (with filters)
GET  /jobs/count    Total job count
```
- Global dataset; Israel-only focus planned
- Browse and filter jobs
- No user accounts, alerts, or apply flows yet
- Add Israel-focused sources and manual curation
- Stronger deduplication and normalization
- Saved filters and lightweight alerts (optional)
```bash
pip install -r requirements.txt
uvicorn jobpulse_api.main:app --app-dir src --host 127.0.0.1 --port 8010
```
---
*MVP focused on solving job search noise for the Israeli market*
