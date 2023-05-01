import contextlib
import logging
from typing import Optional

import structlog

from structlog_asgi.config import _build_default_processors


class UvicornDefaultConsoleFormatter(structlog.stdlib.ProcessorFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=_build_default_processors(json_format=False),
        )


class UvicornAccessConsoleFormatter(structlog.stdlib.ProcessorFormatter):
    def __init__(self, *args, **kwargs):
        processors = [
            _extract_uvicorn_request_meta,
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ]

        # pass_foreign_args чтобы прокидывались значения из record.args в positional_args
        super().__init__(
            processors=processors,
            foreign_pre_chain=_build_default_processors(json_format=False),
            pass_foreign_args=True,
        )


class UvicornDefaultJSONFormatter(structlog.stdlib.ProcessorFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=_build_default_processors(json_format=True),
        )


class UvicornAccessJSONFormatter(structlog.stdlib.ProcessorFormatter):
    def __init__(self, *args, **kwargs):
        processors = [
            _extract_uvicorn_request_meta,
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ]

        # pass_foreign_args чтобы прокидывались значения из record.args в positional_args
        super().__init__(
            processors=processors,
            foreign_pre_chain=_build_default_processors(json_format=True),
            pass_foreign_args=True,
        )


def build_uvicorn_log_config(level=logging.INFO, json_format: bool = False):
    level_name = logging.getLevelName(level)

    if json_format:
        default = UvicornDefaultJSONFormatter
        access = UvicornAccessJSONFormatter
    else:
        default = UvicornDefaultConsoleFormatter
        access = UvicornAccessConsoleFormatter

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": default,
            },
            "access": {
                "()": access,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": level_name,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": level_name,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": level_name,
                "propagate": False,
            },
        },
    }


def _extract_uvicorn_request_meta(
    wrapped_logger: Optional[logging.Logger], method_name: str, event_dict
):
    with contextlib.suppress(KeyError, ValueError):
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = event_dict["positional_args"]

        event_dict["client_addr"] = client_addr
        event_dict["http_method"] = method
        event_dict["url"] = full_path
        event_dict["http_version"] = http_version
        event_dict["status_code"] = status_code

        del event_dict["positional_args"]

    return event_dict
