"""
Structured-ish logging setup. Not pulling in structlog as a dependency —
a plain logging.Formatter that emits one-line, greppable, timestamped
records covers the "add real logging" need without adding weight.
"""

import logging
import sys

from backend.app.core.config import LOG_LEVEL

_CONFIGURED = False


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s :: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.handlers = [handler]

    # Quiet down noisy third-party loggers a bit
    logging.getLogger("uvicorn.access").setLevel(LOG_LEVEL)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
