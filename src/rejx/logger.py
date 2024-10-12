from __future__ import annotations

import logging
import os

from rich.logging import RichHandler

__all__ = ["logger", "setup_logger"]


def setup_logger() -> None:
    logging.basicConfig(
        level=os.getenv("REJX_LOG_LEVEL", logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


logger = logging.getLogger("rich")
