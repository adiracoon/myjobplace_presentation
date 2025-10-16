**Live:** https://app.myjobplace.app &nbsp;&nbsp;•&nbsp;&nbsp; **API docs:** `/docs`, `/redoc`  
> **Note:** the UI text is in Hebrew.
![JobPulse UI](docs/screenshot.png)
LinkedIn & generic boards flood you with loosely relevant roles.  
I wanted a **tighter, precise** feed with clear filters and fast search.
Public career pages + ATS APIs (Greenhouse, Lever, …) → one DB.  
FastAPI backend exposes a clean API; static UI provides search & filters.
Accurate, low-noise coverage of Israeli tech roles with dedup & smart filters.
- FastAPI (`src/` layout) • `/health`, `/readyz`  
- `/jobs` list / count / create / update / soft-delete (filters & paging)  
- Alembic migrations & smoke CI (health-only)
~~~bash
pip install -r requirements.txt
uvicorn jobpulse_api.main:app --app-dir src --host 127.0.0.1 --port 8010
~~~
