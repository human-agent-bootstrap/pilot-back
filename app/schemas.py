"""Request and response models for Task Board API v1."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from app.db import OPEN_STATUS

# The contract normalizes a title by trimming exactly these code points, not every
# character Python considers whitespace.
TITLE_TRIM_CHARS = " \t\n\r"
TITLE_MIN_LENGTH = 1
TITLE_MAX_LENGTH = 100


class TaskCreate(BaseModel):
    """POST /api/tasks request body: the title field and nothing else."""

    model_config = ConfigDict(extra="forbid")

    title: str

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = value.strip(TITLE_TRIM_CHARS)
        # len() counts Unicode code points, which is the unit the contract uses.
        if not TITLE_MIN_LENGTH <= len(normalized) <= TITLE_MAX_LENGTH:
            raise ValueError("title must be 1-100 code points after trimming")
        return normalized


class Task(BaseModel):
    """A stored task."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"id": 1, "title": "첫 작업", "status": OPEN_STATUS}]}
    )

    id: int
    title: str
    status: Literal["open"]


class TaskList(BaseModel):
    """GET /api/tasks response body."""

    items: list[Task]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Error response body for 422 and 500."""

    error: ErrorDetail
