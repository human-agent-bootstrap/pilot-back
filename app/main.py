"""Task Board API v1 — see changes/CHG-TASK-001/contracts/tasks-api.md in the root repository."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import db
from app.schemas import ErrorResponse, Task, TaskCreate, TaskList

FRONTEND_ORIGIN = "http://127.0.0.1:5173"

INVALID_REQUEST_BODY = {
    "error": {
        "code": "INVALID_REQUEST",
        "message": "제목은 공백을 제외한 1~100자 문자열이어야 합니다.",
    }
}
INTERNAL_ERROR_BODY = {
    "error": {"code": "INTERNAL_ERROR", "message": "작업을 처리하지 못했습니다."}
}

_INVALID_REQUEST_RESPONSE = {
    "model": ErrorResponse,
    "description": "Rejected request body. Nothing is stored.",
    "content": {"application/json": {"example": INVALID_REQUEST_BODY}},
}
_INTERNAL_ERROR_RESPONSE = {
    "model": ErrorResponse,
    "description": "Storage or other internal failure.",
    "content": {"application/json": {"example": INTERNAL_ERROR_BODY}},
}

logger = logging.getLogger(__name__)

app = FastAPI(title="Task Board API", version="1.0.0")

# credentials are unused, so the contract's single allowed origin needs no wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)


@app.exception_handler(RequestValidationError)
async def handle_invalid_request(request: Request, exc: RequestValidationError) -> Response:
    """Replace FastAPI's default 422 body with the contract's error envelope.

    This covers a missing, non-string, blank, or too long title, extra fields, and
    unparsable JSON — every case the contract maps to INVALID_REQUEST.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=INVALID_REQUEST_BODY
    )


@app.exception_handler(db.StorageError)
async def handle_storage_error(request: Request, exc: db.StorageError) -> Response:
    logger.exception("task storage failed", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=INTERNAL_ERROR_BODY
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> Response:
    """Safety net so an unforeseen failure still answers with the contract's 500 body."""
    logger.exception("unexpected failure", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=INTERNAL_ERROR_BODY
    )


app.add_exception_handler(Exception, handle_unexpected_error)


@app.get(
    "/api/tasks",
    response_model=TaskList,
    summary="List every task in ascending id order",
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: _INTERNAL_ERROR_RESPONSE},
)
def list_tasks() -> TaskList:
    return TaskList(items=[Task(**task) for task in db.list_tasks()])


@app.post(
    "/api/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    summary="Create one task from a normalized title",
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: _INVALID_REQUEST_RESPONSE,
        status.HTTP_500_INTERNAL_SERVER_ERROR: _INTERNAL_ERROR_RESPONSE,
    },
)
def create_task(payload: TaskCreate) -> Task:
    return Task(**db.create_task(payload.title))
