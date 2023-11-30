import enum
import logging
import sys
from collections.abc import Iterable
from typing import Any, Literal

import structlog
from structlog.typing import Processor
from structlog_sentry import SentryProcessor

from .processors import extract_uvicorn_request_meta, remove_processors_meta


def setup_logging(
    *,
    app_log_level: int = logging.INFO,
    log_level: int = logging.INFO,
    log_format: Literal["plain", "json"],
) -> None:
    logger = logging.getLogger("app")
    logger.setLevel(app_log_level)

    _configure_structlog()
    _configure_default_logging(log_level, log_format)


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _configure_default_logging(
    log_level: int, log_format: Literal["plain", "json"]
) -> None:
    formatter = structlog.stdlib.ProcessorFormatter(
        pass_foreign_args=True,
        processors=_spec(
            [
                extract_uvicorn_request_meta,
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
                structlog.dev.set_exc_info,
                # Must be only in formatter or be duplicated in structlog processors
                # https://www.structlog.org/en/stable/api.html#structlog.processors.CallsiteParameterAdder
                structlog.processors.CallsiteParameterAdder(
                    _spec(
                        [
                            structlog.processors.CallsiteParameter.MODULE,
                            structlog.processors.CallsiteParameter.FUNC_NAME,
                            structlog.processors.CallsiteParameter.THREAD,
                            structlog.processors.CallsiteParameter.THREAD_NAME,
                            structlog.processors.CallsiteParameter.PROCESS,
                            structlog.processors.CallsiteParameter.PROCESS_NAME,
                            _spec_if(
                                structlog.processors.CallsiteParameter.PATHNAME,
                                log_level == logging.DEBUG,
                            ),
                        ]
                    )
                ),
                remove_processors_meta,
                SentryProcessor(
                    level=log_level, event_level=logging.WARNING, verbose=True
                ),
                _spec_if(
                    structlog.processors.dict_tracebacks,
                    log_format == "json",
                ),
                structlog.processors.EventRenamer("message", "event"),
                _make_renderer(log_format),
            ]
        ),
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def _make_renderer(log_format: Literal["plain", "json"]) -> Processor:
    renderers: dict[Literal["plain", "json"], Processor] = {
        "plain": structlog.dev.ConsoleRenderer(
            event_key="message",
            exception_formatter=structlog.dev.better_traceback,
        ),
        "json": structlog.processors.JSONRenderer(),
    }
    return renderers[log_format]


def _spec(items: Iterable[Any]) -> list[Any]:
    return [item for item in items if item != _SKIP]


def _spec_if(item: Any, condition: bool, /) -> Any:  # noqa: FBT001
    if condition:
        return item

    return _SKIP


_SKIP = object()
