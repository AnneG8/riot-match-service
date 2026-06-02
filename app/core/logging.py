import logging
import sys
from typing import Any

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer

from app.core.config import settings

shared_processors: list[Any] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt='iso', utc=True),
]

console_processors: list[Any] = [
    *shared_processors,
]

json_processors: list[Any] = [
    *shared_processors,
    structlog.processors.dict_tracebacks,
]


def get_renderer() -> JSONRenderer | ConsoleRenderer:
    if settings.debug:
        return ConsoleRenderer()
    return JSONRenderer()


def setup_logging() -> None:
    renderer = get_renderer()

    foreign_processors = (
        console_processors
        if settings.debug
        else json_processors
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=foreign_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    log_level = logging.DEBUG if settings.debug else logging.INFO
    root_logger.setLevel(log_level)

    logging.getLogger('httpcore').setLevel(logging.INFO)

    structlog.configure(
        processors=[
            *foreign_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
