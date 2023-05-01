import logging

import structlog_asgi
from structlog_asgi.integrations.gunicorn.logger import StubbedGunicornLogger
from structlog_asgi.integrations.gunicorn.worker import GunicornStandaloneApplication


def run():
    level = logging.DEBUG
    json_format = False
    structlog_asgi.configure(level=level, json_format=json_format)
    worker_class = "structlog_asgi.integrations.uvicorn.worker.StructlogUvicornWorker"
    options = {
        "bind": "0.0.0.0",
        "workers": 1,
        "loglevel": logging.getLevelName(level),
        "worker_class": worker_class,
        "logger_class": StubbedGunicornLogger,
    }

    from examples.asgi_app import app

    GunicornStandaloneApplication(app, options).run()


if __name__ == "__main__":
    run()
