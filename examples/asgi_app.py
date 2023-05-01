"""
Structlog example configuration with FastAPI.
Features:
- async bound logger
- contextvars to log request-id and other meta data
- custom format for default logging loggers and structlog loggers
"""

import asyncio
import logging
import uuid
from contextvars import ContextVar
from threading import Thread
from typing import Any, Optional

import structlog
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.requests import Request
from starlette.responses import Response


structlog_logger = structlog.stdlib.get_logger("structlog")
default_logger = logging.getLogger("default_logger")


default_logger.warning("log in module")

app = FastAPI()

request_id = ContextVar("request_id")


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    value = request.headers.get("request-id", str(uuid.uuid4()))

    request_id.set(value)

    structlog_logger.debug("extract request id header", request_id=value)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=value,
    )

    response: Response = await call_next(request)

    return response


@app.get("/log", response_class=PlainTextResponse)
async def log(q: Optional[str] = None) -> Any:
    default_logger.info(
        "processing request", extra={"q": q, "request_id": request_id.get()}
    )

    async def create_task():
        default_logger.warning("processing task")

    task = asyncio.create_task(create_task())

    def sum_numbers(numbers):
        result = sum(numbers)
        default_logger.warning("numbers sum", extra={"result": result})

    t = Thread(target=sum_numbers, args=(list(range(5)),))
    t.start()

    await task
    t.join()

    return "pong"


@app.get("/slog", response_class=PlainTextResponse)
async def log(q: Optional[str] = None) -> Any:
    structlog_logger.info("processing request", q=q)

    async def create_task():
        structlog_logger.debug("processing task")

    task = asyncio.create_task(create_task())

    def sum_numbers(numbers):
        result = sum(numbers)
        structlog_logger.debug("numbers sum", result=result)

    t = Thread(target=sum_numbers, args=(list(range(5)),))
    t.start()

    await task
    t.join()

    return "pong"


@app.get("/exc", response_class=PlainTextResponse)
async def exc() -> Any:
    print(logging.getLogger("uvicorn.error").handlers)
    try:
        print(logging.getLogger("uvicorn.error").handlers[0].formatter)
    except:
        pass
    raise RuntimeError("boom")


@app.get("/error", response_class=PlainTextResponse)
async def error() -> Any:
    try:
        1 / 0
    except ZeroDivisionError:
        default_logger.exception("booooooooom")
