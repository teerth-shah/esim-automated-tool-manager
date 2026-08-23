"""Logging setup and accessor for eSim Tool Manager."""

import logging
from pathlib import Path
from typing import Optional, Union

_LOGGER: Optional[logging.Logger] = None
LOGGER_NAME = "esim_tool_manager"


def setup_logger(
    log_dir: Union[str, Path] = "logs",
    log_filename: str = "tool_manager.log",
) -> logging.Logger:
    """Configure and return the tool manager logger.

    Args:
        log_dir: Directory path where log files will be written.
        log_filename: Name of the log file.

    Returns:
        Configured logging.Logger instance.
    """
    global _LOGGER

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / log_filename

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    _LOGGER = logger
    return logger


def get_logger() -> logging.Logger:
    """Return the singleton logger instance, configuring with defaults if uninitialized."""
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = setup_logger()
    return _LOGGER
