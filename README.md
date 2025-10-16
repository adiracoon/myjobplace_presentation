**Live:** [https://app.myjobplace.app](https://app.myjobplace.app)
<p align="center">
  <a href="[https://app.myjobplace.app](https://app.myjobplace.app)">
    <img src="docs/screenshot.png" alt="JobPulse UI" width="900" />
  </a>
</p>
Generic job boards create a noisy firehose. I wanted a **precise, low-noise feed** so candidates spend less time sifting.
An MVP that **aggregates public company career pages and ATS sources** (e.g., Greenhouse, Lever) into one API with a simple **Hebrew UI** for fast filtering (title, company, location).
- Global dataset; **Israel-only focus planned**.
- Browse & filter; **no** accounts, alerts, or apply flows.
- Add Israel-focused sources and manual curation.
- Stronger dedup/normalization across sources.
- Saved filters / lightweight alerts (optional).
- **Endpoints:** `GET /health`, `GET /readyz`, `GET /jobs`, `GET /jobs/count`
- **Tech:** FastAPI · SQLModel · Alembic · Vanilla JS (static assets)
```bash
pip install -r requirements.txt
uvicorn jobpulse_api.main:app --app-dir src --host 127.0.0.1 --port 8010
```
