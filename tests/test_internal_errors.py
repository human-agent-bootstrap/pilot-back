"""Storage failures answer with the contract's 500 envelope and leak no internals."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app

INTERNAL_ERROR_BODY = {
    "error": {"code": "INTERNAL_ERROR", "message": "작업을 처리하지 못했습니다."}
}


def _fail(*args: object, **kwargs: object) -> None:
    raise db.StorageError("sqlite3.OperationalError: disk I/O error at /secret/path.sqlite3")


def test_list_storage_failure_returns_500_envelope(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(db, "list_tasks", _fail)

    response = client.get("/api/tasks")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == INTERNAL_ERROR_BODY


def test_create_storage_failure_returns_500_envelope(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(db, "create_task", _fail)

    response = client.post("/api/tasks", json={"title": "첫 작업"})

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR_BODY


def test_500_body_hides_the_db_path_and_exception_detail(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, db_file: Path
) -> None:
    monkeypatch.setattr(db, "create_task", _fail)

    body = client.post("/api/tasks", json={"title": "첫 작업"}).text

    assert str(db_file) not in body
    assert "sqlite3" not in body
    assert "secret" not in body
    assert "Traceback" not in body


def test_unopenable_database_returns_500_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A real SQLite failure, not a patched one: the path points at a directory."""
    monkeypatch.setenv("TASK_DB_PATH", str(tmp_path))

    with TestClient(app) as client:
        response = client.get("/api/tasks")

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR_BODY


def test_unexpected_exception_returns_500_envelope(
    db_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Failures other than StorageError also answer with the contract body."""

    def raise_runtime_error(*args: object, **kwargs: object) -> None:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(db, "list_tasks", raise_runtime_error)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/tasks")

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR_BODY
