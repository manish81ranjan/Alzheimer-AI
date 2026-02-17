# backend/src/utils/logger.py
"""
Central logging utility.

- Consistent log format
- Works locally and on Render
- Avoids print() scattered everywhere
"""

import logging
import sys


def setup_logger(name: str = "alzheimer-ai", level: int = logging.INFO) -> logging.Logger:
    """
    Create or return a configured logger.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    return logger
