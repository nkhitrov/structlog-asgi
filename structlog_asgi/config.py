# https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
# https://www.youtube.com/watch?v=yZD0YprGIko&t=1454s
# https://florian-dahlitz.de/articles/logging-made-easy-with-loguru
# https://www.zopatista.com/python/2019/05/11/asyncio-logging/
# https://github.com/wimglenn/pytest-structlog/blob/main/pytest_structlog.py
# https://stackoverflow.com/questions/9534245/python-logging-to-stringio-handler


# https://inboard.bws.bio/logging
# https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block
# https://docs.python.org/3/howto/logging-cookbook.html#running-a-logging-socket-listener-in-production
# https://docs.python.org/3/howto/logging-cookbook.html#buffering-logging-messages-and-outputting-them-conditionally
# https://docs.python.org/3/howto/logging-cookbook.html#using-loggers-as-attributes-in-a-class-or-passing-them-as-parameters
# https://bitestreams.com/blog/structured_logging/
# https://github.com/sqlalchemy/sqlalchemy-collectd

import logging
import sys

import structlog


def configure(level=logging.INFO, json_format: bool = False):
    _configure_structlog(json_format)
    _configure_default_logging(level=level, json_format=json_format)


def _build_default_processors(json_format):
    pr = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.THREAD,
                structlog.processors.CallsiteParameter.THREAD_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            }
        ),
    ]
    if json_format:
        pr.append(structlog.processors.format_exc_info)

    return pr


def _configure_structlog(json_format):
    structlog.configure_once(
        processors=_build_default_processors(json_format=json_format)
        + [
            # used for integration with default logging
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def _configure_default_logging(*, level, json_format: bool):
    renderer_processor = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer()
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=_build_default_processors(json_format=json_format)
        + [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer_processor,
        ],
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
