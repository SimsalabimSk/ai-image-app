from __future__ import annotations

import logging
import sys
from pythonjsonlogger import jsonlogger


def configure_json_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    # Clear default handlers
    logger.handlers = []
    logger.addHandler(handler)
