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

    db_path = Path(__file__).resolve().parent.parent / "data" / "board.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            if "posts" in tables:
                columns = {row[1] for row in conn.execute("PRAGMA table_info(posts)").fetchall()}
                if "location_id" in columns or "category" in columns:
                    conn.execute("DROP TABLE posts")
                    conn.commit()

    Base.metadata.create_all(bind=engine)


ensure_schema()
