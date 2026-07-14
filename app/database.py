import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "board.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '서울',
                password TEXT NOT NULL DEFAULT '',
                view_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        columns = {row[1] for row in conn.execute("PRAGMA table_info(posts)").fetchall()}
        if "category" not in columns:
            conn.execute("ALTER TABLE posts ADD COLUMN category TEXT NOT NULL DEFAULT '서울'")
        if "password" not in columns:
            conn.execute("ALTER TABLE posts ADD COLUMN password TEXT NOT NULL DEFAULT ''")
        if "view_count" not in columns:
            conn.execute("ALTER TABLE posts ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0")

        conn.commit()
