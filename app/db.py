"""SQLite storage for tasks.

The database file comes from TASK_DB_PATH and is read on every call so a process can be
pointed at another file without reimporting the module. Storage failures are raised as
StorageError; the API layer turns that into the contract's INTERNAL_ERROR response without
exposing the path or the underlying exception.
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = "./data/tasks.sqlite3"
OPEN_STATUS = "open"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT NOT NULL
)
"""


class StorageError(Exception):
    """A task could not be read from or written to SQLite."""


def db_path() -> Path:
    return Path(os.environ.get("TASK_DB_PATH") or DEFAULT_DB_PATH)


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute(_SCHEMA)
        yield connection
    finally:
        connection.close()


def list_tasks() -> list[dict[str, object]]:
    """Return every stored task in ascending id order."""
    try:
        with _connect() as connection:
            rows = connection.execute(
                "SELECT id, title, status FROM tasks ORDER BY id ASC"
            ).fetchall()
    except (OSError, sqlite3.Error) as exc:
        raise StorageError("failed to read tasks") from exc
    return [dict(row) for row in rows]


def create_task(title: str) -> dict[str, object]:
    """Store one task with the already normalized title and return it."""
    try:
        with _connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, status) VALUES (?, ?)", (title, OPEN_STATUS)
            )
            connection.commit()
            task_id = cursor.lastrowid
    except (OSError, sqlite3.Error) as exc:
        raise StorageError("failed to store a task") from exc
    return {"id": int(task_id), "title": title, "status": OPEN_STATUS}
