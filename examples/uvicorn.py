# https://www.structlog.org/en/21.2.0/loggers.html#creation
import logging

import structlog_asgi
import uvicorn


def run():
    structlog_asgi.setup_logging(log_level=logging.DEBUG, log_format="json")

    from examples.asgi_app import app

    uvicorn.run(app=app, log_config=None)


if __name__ == "__main__":
    run()
