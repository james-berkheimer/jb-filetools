import logging

import colorlog

# Define a new log level for user interaction (Questions)
QUESTION = 25
logging.addLevelName(QUESTION, "QUESTION")


def question(self, message, *args, **kwargs):
    """Custom log method for handling user questions."""
    if self.isEnabledFor(QUESTION):
        self._log(QUESTION, message, args, **kwargs)


logging.Logger.question = question  # Add to logger class


def setup_logger(name=None, level=logging.INFO):
    """Return a logger with a default ColoredFormatter."""
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:%(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "QUESTION": "blue",  # Custom color for questions
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    if name:
        logger = colorlog.getLogger(name)
    else:
        logger = logging.getLogger()

    # Check if the logger already has handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)

    return logger
