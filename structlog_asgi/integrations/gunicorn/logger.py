import logging

from gunicorn.glogging import Logger


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        print(cfg.loglevel)
        _nameToLevel = {
            "CRITICAL": logging.CRITICAL,
            "FATAL": logging.FATAL,
            "ERROR": logging.ERROR,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }

        self.loglevel = _nameToLevel[cfg.loglevel]
        self.error_log.setLevel(self.loglevel)
        self.access_log.setLevel(self.loglevel)
