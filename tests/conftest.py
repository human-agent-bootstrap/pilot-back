from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def db_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the storage layer at a per-test SQLite file under a not yet existing directory."""
    path = tmp_path / "data" / "tasks.sqlite3"
    monkeypatch.setenv("TASK_DB_PATH", str(path))
    return path


@pytest.fixture
def client(db_file: Path) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
