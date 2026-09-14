import logging
import logging.handlers
import os
import sys
from datetime import datetime

# ---------- Config ----------
LOG_DIR = "logs"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"

# Create logs dir if missing
os.makedirs(LOG_DIR, exist_ok=True)

# ---------- Formats ----------
CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ---------- Root Logger ----------
def setup_logging():
    root = logging.getLogger()
    if root.handlers:          # avoid duplicate handlers on re-import
        return root

    root.setLevel(LOG_LEVEL)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT, DATE_FORMAT))
    root.addHandler(console)

    # File handler (rotating)
    if LOG_TO_FILE:
        log_file = os.path.join(LOG_DIR, f"app_{datetime.now():%Y-%m-%d}.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))
        root.addHandler(file_handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "httpx", "httpcore", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return root


def get_logger(name: str) -> logging.Logger:
    """Use this everywhere: logger = get_logger(__name__)"""
    return logging.getLogger(name)