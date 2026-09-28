import sqlite3

from pathlib import Path
from contextlib import contextmanager

from app.config import settings


def _db_path() -> str:
    prefix = "sqlite:///"

    if settings.database_url.startswith(prefix):
        return settings.database_url[len(prefix):]

    return settings.database_url


def init_db() -> None:
    path = Path(_db_path())

    if not path.is_absolute():
        path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner_type TEXT NOT NULL,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL,
                saved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
            );
            """
        )

        # Add saved column if an older database already exists
        columns = conn.execute(
            "PRAGMA table_info(recommendations)"
        ).fetchall()

        column_names = [column[1] for column in columns]

        if "saved" not in column_names:
            conn.execute(
                """
                ALTER TABLE recommendations
                ADD COLUMN saved INTEGER NOT NULL DEFAULT 0
                """
            )


@contextmanager
def get_db():
    path = Path(_db_path())

    conn = sqlite3.connect(path)

    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()

    finally:
        conn.close()