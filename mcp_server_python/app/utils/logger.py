"""
Logger utility for the MCP server
"""

import logging
import os
import sys
from typing import Any, Dict, Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler

from app.core.config import settings

# Ensure log directory exists
log_dir = os.path.dirname(settings.LOG_FILE) if settings.LOG_FILE else "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)


def configure_logging() -> None:
    """
    Configure logging for the application
    """
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if not settings.STRUCTURED_LOGGING else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = []
    
    # Console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        console=Console(stderr=True),
        tracebacks_show_locals=settings.DEBUG,
    )
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # File handler if log file is specified
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(log_level)
        
        if settings.STRUCTURED_LOGGING:
            file_handler.setFormatter(logging.Formatter('{"timestamp":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}'))
        else:
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )
    
    # Set log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger

    Args:
        name: Optional logger name

    Returns:
        A structured logger
    """
    return structlog.get_logger(name)


class Logger:
    """
    Logger class that can be used as a dependency
    """
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        self.logger = get_logger()
        if context:
            self.logger = self.logger.bind(**context)

    def bind(self, **kwargs: Any) -> "Logger":
        """Bind additional context to the logger"""
        self.logger = self.logger.bind(**kwargs)
        return self

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message"""
        self.logger.critical(message, **kwargs)


# Initialize logging when module is imported
configure_logging()