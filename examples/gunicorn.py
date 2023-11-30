import logging

import structlog_asgi
from structlog_asgi.integrations.gunicorn.logger import StubbedGunicornLogger
from structlog_asgi.integrations.gunicorn.worker import GunicornStandaloneApplication


def run():
    level = logging.DEBUG
    structlog_asgi.setup_logging(log_level=level, log_format="plain")
    options = {
        "bind": "0.0.0.0",
        "workers": 1,
        "loglevel": logging.getLevelName(level),
        # "worker_class": "structlog_asgi.integrations.gunicorn.StructlogUvicornWorker",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    from examples.asgi_app import app

    GunicornStandaloneApplication(app, options).run()


if __name__ == "__main__":
    run()
