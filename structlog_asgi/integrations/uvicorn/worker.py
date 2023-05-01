import logging

from uvicorn.workers import UvicornWorker

from structlog_asgi.integrations.uvicorn import build_uvicorn_log_config


class StructlogUvicornWorker(UvicornWorker):
    level: int = logging.DEBUG
    json_format: bool = False

    def __init__(self, *args, **kwargs):
        self.CONFIG_KWARGS["log_config"] = build_uvicorn_log_config(
            level=self.level, json_format=self.json_format
        )
        super().__init__(*args, **kwargs)
