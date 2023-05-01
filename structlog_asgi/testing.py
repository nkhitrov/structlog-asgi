import contextlib

import pytest
import structlog
from structlog.testing import LogCapture


@contextlib.contextmanager
def capture_full_logs():
    """Copy of structlog.testing.capture_logs() but without processors clearing."""
    cap = LogCapture()

    processors = structlog.get_config()["processors"]
    old_processors = processors.copy()
    try:
        # wrapper change dict tu tuple for logging
        with contextlib.suppress(ValueError):
            processors.remove(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

        processors.append(cap)
        structlog.configure(processors=processors)
        yield cap.entries
    finally:
        # remove LogCapture and restore original processors
        processors.clear()
        processors.extend(old_processors)
        structlog.configure(processors=processors)
