import logging
import sys
from typing import Any, Dict


def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Configures structured logging without leaking sensitive information."""
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


logger = logging.getLogger("lotm_tarot")
