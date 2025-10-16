# JobPulse 🔍

**A precise, low-noise job aggregator for the Israeli tech market**

🔗 **Live:** [https://app.myjobplace.app](https://app.myjobplace.app)

<p align="center">
  <a href="https://app.myjobplace.app">
    <img src="docs/screenshot.png" alt="JobPulse Interface" width="800" />
  </a>
</p>

## 📋 Overview
Generic job boards create a noisy firehose. JobPulse is an MVP that aggregates public company career pages and ATS sources (e.g., Greenhouse, Lever) into one API, with a simple **Hebrew UI** for quick browsing and filtering.

### 🎯 Problem We Solve
Candidates spend too much time sifting through loosely relevant roles. The goal is a **precise, low-noise feed** so people waste less time.

### ✨ Key Features
- **Direct from source** – pulls from public company career pages/ATS
- **Lower noise** – basic freshness and de-dup signals (MVP level)
- **Fast browsing & filters** – UI filters by title/company/location
- **Hebrew UI** – localized interface
- **No accounts** – open access, no signup required

## 🛠️ Tech Stack

### Backend
- **FastAPI** (Python)
- **SQLModel** + **SQLAlchemy**
- **Alembic** for migrations

### Frontend
- **Vanilla JS + HTML/CSS** (static assets)

### Database
- **SQLite / PostgreSQL** (configurable via `DATABASE_URL`)

## 🚀 Quick Start
```bash
pip install -r requirements.txt
uvicorn jobpulse_api.main:app --app-dir src --host 127.0.0.1 --port 8010
# open http://127.0.0.1:8010/health
