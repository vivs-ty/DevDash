import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_env_url = os.getenv("DATABASE_URL")
if _env_url:
    SQLALCHEMY_DATABASE_URL = _env_url
    _connect_args: dict = {}
else:
    DB_PATH = Path(__file__).parent.parent / "devdash.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    _connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
