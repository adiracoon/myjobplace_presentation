import os
from typing import Iterator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import make_url
DEFAULT_URL = "sqlite:///./data/jobpulse_dev.sqlite"
def _ensure_sqlite_dir(url_str: str) -> None:
    try:
        u = make_url(url_str)
        if u.get_backend_name().startswith("sqlite") and u.database:
            parent = os.path.dirname(u.database)
            if parent:
                os.makedirs(parent, exist_ok=True)
    except Exception:
        pass
def _create_engine_from_env():
    url = os.getenv("DATABASE_URL", DEFAULT_URL)
    _ensure_sqlite_dir(url)
    return create_engine(url, echo=False, future=True)
def init_db() -> None:
    from jobpulse_api import models as _models  # noqa: F401
    engine = _create_engine_from_env()
    with engine.begin() as conn:
        SQLModel.metadata.create_all(conn)
    try:
        u = make_url(os.getenv("DATABASE_URL", DEFAULT_URL))
        if u.get_backend_name().startswith("sqlite") and u.database and not os.path.exists(u.database):
            open(u.database, "a").close()
    except Exception:
        pass
def get_session() -> Iterator[Session]:
    engine = _create_engine_from_env()
    with Session(engine) as session:
        yield session
