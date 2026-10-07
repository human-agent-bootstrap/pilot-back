"""Every request body the contract maps to a 422 INVALID_REQUEST response."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

INVALID_REQUEST_BODY = {
    "error": {
        "code": "INVALID_REQUEST",
        "message": "제목은 공백을 제외한 1~100자 문자열이어야 합니다.",
    }
}

INVALID_PAYLOADS: dict[str, Any] = {
    "missing_title": {},
    "null_title": {"title": None},
    "integer_title": {"title": 1},
    "boolean_title": {"title": True},
    "list_title": {"title": ["첫 작업"]},
    "object_title": {"title": {"value": "첫 작업"}},
    "empty_title": {"title": ""},
    "space_only_title": {"title": " "},
    "tab_only_title": {"title": "\t"},
    "lf_only_title": {"title": "\n"},
    "cr_only_title": {"title": "\r"},
    "all_trim_chars_title": {"title": " \t\n\r"},
    "title_over_100_code_points": {"title": "가" * 101},
    "extra_field": {"title": "첫 작업", "status": "open"},
    "unknown_field": {"title": "첫 작업", "done": False},
    "title_absent_but_other_field_present": {"name": "첫 작업"},
}


@pytest.mark.parametrize("payload", INVALID_PAYLOADS.values(), ids=list(INVALID_PAYLOADS))
def test_invalid_payload_returns_422_envelope(client: TestClient, payload: Any) -> None:
    response = client.post("/api/tasks", json=payload)

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == INVALID_REQUEST_BODY


@pytest.mark.parametrize("payload", INVALID_PAYLOADS.values(), ids=list(INVALID_PAYLOADS))
def test_invalid_payload_stores_nothing(client: TestClient, payload: Any) -> None:
    client.post("/api/tasks", json=payload)

    assert client.get("/api/tasks").json() == {"items": []}


@pytest.mark.parametrize("body", ["", "{", "{'title': '첫 작업'}", "not json at all"])
def test_unparsable_json_returns_422_envelope(client: TestClient, body: str) -> None:
    response = client.post("/api/tasks", content=body, headers={"Content-Type": "application/json"})

    assert response.status_code == 422
    assert response.json() == INVALID_REQUEST_BODY
    assert client.get("/api/tasks").json() == {"items": []}


def test_a_valid_request_after_rejections_still_gets_id_1(client: TestClient) -> None:
    """Rejected requests must not consume an id, because nothing is stored."""
    client.post("/api/tasks", json={"title": " "})
    client.post("/api/tasks", json={"title": "가" * 101})

    response = client.post("/api/tasks", json={"title": "첫 작업"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "첫 작업", "status": "open"}
