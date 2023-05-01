# https://habr.com/ru/articles/513966/
# 7. Исключения в процессе журналирования
# сделать обработчик ошибок логера, который будет отсылать в сентри

import logging
import multiprocessing
import os
from logging.handlers import QueueHandler, QueueListener
import sys

formatter = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(process)d %(processName)s %(threadName)s - %(message)s"


def log_producer():
    pid = os.getpid()
    logger = logging.getLogger(__name__)
    logger.info(f"pid {pid}")


def main():
    queue = multiprocessing.Queue(-1)
    handler = QueueHandler(queue)

    logging.basicConfig(
        level=logging.INFO, format=formatter, handlers=[handler], force=True
    )

    root_logger = logging.getLogger()

    root_logger.addHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    queue_listener = QueueListener(queue, stream_handler)
    queue_listener.start()

    workers = []
    for i in range(2):
        worker = multiprocessing.Process(target=log_producer)
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()
    queue_listener.stop()


if __name__ == "__main__":
    main()
