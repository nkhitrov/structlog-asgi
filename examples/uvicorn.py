# https://www.structlog.org/en/21.2.0/loggers.html#creation
import logging

import structlog_asgi
import uvicorn


def run():
    level = logging.DEBUG
    json_format = False
    structlog_asgi.configure(level=level, json_format=json_format)

    log_config = structlog_asgi.build_uvicorn_log_config(
        level=level, json_format=json_format
    )
    from examples.asgi_app import app

    uvicorn.run(app=app, log_config=log_config, use_colors=False)


if __name__ == "__main__":
    run()
