import logging
from typing import Optional

import colorlog

# Define custom log levels
QUESTION = 25

logging.addLevelName(QUESTION, "QUESTION")


# def question(self, message, *args, **kwargs) -> None:
#     """Custom log method for handling user questions with "|| " prefix."""
#     if self.isEnabledFor(QUESTION):
#         self._log(QUESTION, message, args, **kwargs)


# logging.Logger.question = question  # Add to logger class


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger with colored output formatting.

    Sets up a logger with two handlers:
    1. Info/Question handler: Uses "|| " prefix without level name
    2. Standard handler: Uses "|| " prefix with level name for other log levels

    Args:
        name: The name of the logger. Defaults to "filetools" if None
        level: The logging level to set. Defaults to logging.INFO

    Returns:
        logging.Logger: Configured logger instance with colored formatting
    """
    # Use a consistent logger name
    logger = colorlog.getLogger(name) if name else logging.getLogger("filetools")

    # Prevent duplicate handlers across different modules
    if logger.hasHandlers():
        logger.setLevel(level)
        return logger

    # Define formatter with "|| " prefix for INFO & QUESTION (no level name)
    info_question_formatter = colorlog.ColoredFormatter(
        "%(log_color)s|| %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "INFO": "white",
            "QUESTION": "green",
        },
        secondary_log_colors={},
        style="%",
    )

    # Define standard formatter with "|| " + levelname
    standard_formatter = colorlog.ColoredFormatter(
        "%(log_color)s|| %(levelname)s: %(reset)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    # Create separate handlers for INFO/QUESTION and other levels
    info_question_handler = logging.StreamHandler()
    info_question_handler.setFormatter(info_question_formatter)
    info_question_handler.addFilter(lambda record: record.levelno in (logging.INFO, QUESTION))

    standard_handler = logging.StreamHandler()
    standard_handler.setFormatter(standard_formatter)
    standard_handler.addFilter(lambda record: record.levelno not in (logging.INFO, QUESTION))

    # Attach handlers to the logger
    logger.addHandler(info_question_handler)
    logger.addHandler(standard_handler)

    logger.setLevel(level)

    return logger
