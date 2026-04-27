"""
Singleton logger for VibeMatch.

All modules import get_logger() from here. First call creates the logger
and attaches handlers; subsequent calls return the same instance.

Log levels:
  - INFO and above → logs/vibematch_YYYYMMDD.log
  - WARNING and above → stderr (console)
"""

import logging
import os
from datetime import datetime

_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    """Return the shared VibeMatch logger, initializing it on first call."""
    global _logger
    if _logger is not None:
        return _logger

    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/vibematch_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("vibematch")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        console_fmt = logging.Formatter("[%(levelname)s] %(message)s")

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_fmt)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_fmt)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    _logger = logger
    return _logger
