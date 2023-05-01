import logging
from datetime import datetime, timedelta

import structlog
from assertpy import assert_that

import structlog_asgi
from structlog_asgi import capture_full_logs
from tests.support import read_json_logs


class TestJSONConfiguration:
    @staticmethod
    def test_log(capfd):
        structlog_asgi.configure(json_format=True)

        logger = structlog.get_logger("testlogger")
        logger.info("simple message")
        logger.info(
            "kwargs message",
            test_int=123,
            test_str="params",
            test_dict={"key": "value"},
        )

        simple_log, kwargs_log = read_json_logs(capfd)

        assert_that(simple_log).is_equal_to(
            {
                "event": "simple message",
                "filename": "test_default_configuration.py",
                "func_name": "test_log",
                "level": "info",
                "logger": "testlogger",
                "module": "test_default_configuration",
                "thread_name": "MainThread",
            },
            ignore=["timestamp", "thread", "process", "pathname", "process_name"],
        )

        assert_that(kwargs_log).is_equal_to(
            {
                "event": "kwargs message",
                "filename": "test_default_configuration.py",
                "func_name": "test_log",
                "level": "info",
                "logger": "testlogger",
                "module": "test_default_configuration",
                "test_dict": {"key": "value"},
                "test_int": 123,
                "test_str": "params",
                "thread_name": "MainThread",
            },
            ignore=["timestamp", "thread", "process", "pathname", "process_name"],
        )

        assert_that(simple_log).contains_key(
            "timestamp", "thread", "process", "pathname", "process_name"
        )
        assert_that(kwargs_log).contains_key(
            "timestamp", "thread", "process", "pathname", "process_name"
        )

    @staticmethod
    def test_timestamp_format(capfd):
        structlog_asgi.configure(json_format=True)

        logger = structlog.get_logger()
        with capture_full_logs() as cap_logs:
            logger.info("simple message")

        now = datetime.utcnow()

        [simple_log] = cap_logs

        raw_timestamp = simple_log["timestamp"].replace("Z", "+00:00")
        timestamp = datetime.fromisoformat(raw_timestamp).replace(tzinfo=None)

        assert_that(timestamp).is_close_to(now, timedelta(seconds=2))

    @staticmethod
    def test_filter_logs_by_level(capfd):
        structlog_asgi.configure(level=logging.WARNING, json_format=True)

        logger = structlog.get_logger("testlogger")
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")

        messages = read_json_logs(capfd)

        assert_that(messages).extracting("level").contains_only("warning", "error")
