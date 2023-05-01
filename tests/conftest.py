import logging

import pytest
import structlog

ROOT_LOGGER = logging.getLogger()

# TODO logging caplog
# https://github.com/encode/uvicorn/blob/d43afed1cfa018a85c83094da8a2dd29f656d676/tests/middleware/test_logging.py#L24


@pytest.fixture(autouse=True)
def _ensure_logging_framework_not_altered():
    """
    Prevents 'ValueError: I/O operation on closed file.' errors.
    """
    before_handlers = list(ROOT_LOGGER.handlers)

    yield

    ROOT_LOGGER.handlers = before_handlers


@pytest.fixture(autouse=True)
def _reset_structlog_configuration():
    assert structlog.is_configured() is False
    structlog.reset_defaults()

    yield

    structlog.reset_defaults()
    assert structlog.is_configured() is False


@pytest.fixture(autouse=True)
def _reset_logging_configuration():
    logging.basicConfig(handlers=[], force=True, level=logging.NOTSET)
    yield
    logging.basicConfig(handlers=[], force=True, level=logging.NOTSET)
