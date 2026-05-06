"""
logging_config.py
Structured JSON logging setup for book-app-project.

Usage:
    from logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("event.name", extra={"key": "value"})

Output format (one JSON object per line, written to stderr):
    {"timestamp": "2026-05-06T12:00:00.123456Z", "level": "INFO",
     "logger": "books", "event": "collection.add",
     "title": "Dune", "result": "success", "collection_size": 3}

To suppress logs during normal CLI use:
    LOG_LEVEL=WARNING python book_app.py list

To write logs to a file:
    python book_app.py add 2>>book-app.log
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        # Merge any extra fields passed via logger.info(..., extra={...})
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                payload[key] = value
        return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes structured JSON to stderr."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level_name, logging.INFO))
    return logger
