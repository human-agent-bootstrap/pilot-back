"""CORS behaviour for the single allowed frontend origin."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import FRONTEND_ORIGIN

DISALLOWED_ORIGINS = [
    "http://localhost:5173",  # a different origin from 127.0.0.1 by definition
    "http://127.0.0.1:5174",
    "https://127.0.0.1:5173",
    "http://example.test",
]


def test_preflight_is_allowed_for_the_frontend_origin(client: TestClient) -> None:
    response = client.options(
        "/api/tasks",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    allowed_methods = response.headers["access-control-allow-methods"]
    assert {"GET", "POST", "OPTIONS"} <= {m.strip() for m in allowed_methods.split(",")}
    allowed_headers = response.headers["access-control-allow-headers"]
    assert "content-type" in allowed_headers.lower()
    assert "access-control-allow-credentials" not in response.headers


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_actual_request_is_readable_by_the_frontend_origin(client: TestClient, method: str) -> None:
    response = client.request(
        method,
        "/api/tasks",
        headers={"Origin": FRONTEND_ORIGIN},
        json={"title": "첫 작업"} if method == "POST" else None,
    )

    assert response.status_code in {200, 201}
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert "access-control-allow-credentials" not in response.headers


def test_error_responses_stay_readable_by_the_frontend_origin(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    invalid = client.post("/api/tasks", json={"title": " "}, headers={"Origin": FRONTEND_ORIGIN})

    assert invalid.status_code == 422
    assert invalid.headers["access-control-allow-origin"] == FRONTEND_ORIGIN

    monkeypatch.setattr(db, "list_tasks", _raise_storage_error)
    failed = client.get("/api/tasks", headers={"Origin": FRONTEND_ORIGIN})

    assert failed.status_code == 500
    assert failed.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


def _raise_storage_error(*args: object, **kwargs: object) -> None:
    raise db.StorageError("failed to read tasks")


@pytest.mark.parametrize("origin", DISALLOWED_ORIGINS)
def test_disallowed_origin_gets_no_allow_origin_header(client: TestClient, origin: str) -> None:
    simple = client.get("/api/tasks", headers={"Origin": origin})
    preflight = client.options(
        "/api/tasks",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert "access-control-allow-origin" not in simple.headers
    assert "access-control-allow-origin" not in preflight.headers
