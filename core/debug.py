"""
debug.py - Centralized debug logging with rotation for AnkiScape.

Usage:
- from .debug import debug_log
- Optionally enable via environment ANKISCAPE_DEBUG=1, or call set_debug_enabled(True).

Notes:
- Uses size-based rotation (approx 1MB per file, keep 3 backups): ankiscape_debug.log, .1, .2, .3
- If disabled, debug_log is a no-op and cheap.
"""
from __future__ import annotations

import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# Log file path next to the package (created on demand)
DEBUG_LOG_FILE = os.path.join(os.path.dirname(__file__), "ankiscape_debug.log")

# Default enablement: off unless explicitly enabled
_enabled: bool = os.getenv("ANKISCAPE_DEBUG", "").strip() not in ("", "0", "false", "False")
_logger: Optional[logging.Logger] = None


def _ensure_logger() -> Optional[logging.Logger]:
    global _logger
    if not _enabled:
        return None
    if _logger is not None:
        return _logger

    logger = logging.getLogger("ankiscape.debug")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers on reload
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        try:
            os.makedirs(os.path.dirname(DEBUG_LOG_FILE), exist_ok=True)
            handler = RotatingFileHandler(
                DEBUG_LOG_FILE,
                maxBytes=1_000_000,  # ~1 MB per file
                backupCount=3,       # keep up to 3 rotated files
                encoding="utf-8",
            )
            formatter = logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            # If handler fails (e.g., permission), keep logger without file to avoid crashes
            pass
    _logger = logger
    return _logger


def set_debug_enabled(enabled: bool) -> None:
    """Programmatically enable/disable debug logging for this process."""
    global _enabled, _logger
    _enabled = bool(enabled)
    # Reset logger so it can be recreated with/without handlers
    _logger = None
    _ensure_logger()


def is_debug_enabled() -> bool:
    return _enabled


def debug_log(msg: str) -> None:
    """Write a line to the rotating debug log if enabled; otherwise no-op."""
    if not _enabled:
        return
    try:
        logger = _ensure_logger()
        if logger is not None and logger.handlers:
            logger.info(str(msg))
            return
        # Fallback to direct append if logger couldn't attach a file handler
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} | {msg}\n")
    except Exception:
        # Never raise from debug logging
        pass
