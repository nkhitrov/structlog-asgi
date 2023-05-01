import asyncio
from contextlib import asynccontextmanager

import pytest
from assertpy import assert_that
from fastapi import FastAPI
from uvicorn import Config, Server

import structlog_asgi
from structlog_asgi.integrations.uvicorn import build_uvicorn_log_config
from tests.support import read_json_logs

pytestmark = [pytest.mark.asyncio]


@asynccontextmanager
async def run_server(config: Config):
    """
    Copy of test util from uvicorn repo
    https://github.com/encode/uvicorn/blob/d43afed1cfa018a85c83094da8a2dd29f656d676/tests/utils.py#LL10C11-L10C11
    """
    server = Server(config=config)
    task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.1)
    try:
        yield server
    finally:
        await server.shutdown()
        task.cancel()


async def test_uvicorn_logs_format(capfd):
    app = FastAPI()

    structlog_asgi.configure(json_format=True)

    log_config = build_uvicorn_log_config(json_format=True)

    config = Config(app=app, log_config=log_config)
    async with run_server(config):
        pass

    logs = read_json_logs(capfd)

    started_log, *head = logs

    assert started_log["event"].startswith("Started server process [")
    assert_that(head).extracting("event").is_equal_to(
        [
            "Waiting for application startup.",
            "Application startup complete.",
            "Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)",
            "Shutting down",
            "Waiting for application shutdown.",
            "Application shutdown complete.",
        ]
    )
    assert_that(logs).extracting("logger").contains_only("uvicorn.error")

    assert_that(logs).extracting("thread_name").contains_only("MainThread")
    assert_that(logs).extracting("process_name").contains_only("MainProcess")

    for log in logs:
        assert_that(log).contains_key(
            "filename",
            "module",
            "func_name",
            "timestamp",
            "thread",
            "process",
            "pathname",
        )
