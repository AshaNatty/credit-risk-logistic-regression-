import logging
import json
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for observability."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra", None)
        if extra and isinstance(extra, dict):
            log_entry.update(extra)
        return json.dumps(log_entry)


def configure_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = []
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
