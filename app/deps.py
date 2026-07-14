import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/board.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_schema() -> None:
    from app.models import Base

    Base.metadata.create_all(bind=engine)

    db_path = Path(__file__).resolve().parent.parent / "data" / "board.db"
    if not db_path.exists():
        return

    with sqlite3.connect(db_path) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(posts)").fetchall()}
        if "location_id" not in columns:
            conn.execute("ALTER TABLE posts ADD COLUMN location_id INTEGER NOT NULL DEFAULT 1")
        conn.commit()


ensure_schema()
