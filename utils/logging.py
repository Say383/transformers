# utils/logging.py

import logging


def log_info(message: str):
    """Log an informational message."""
    logging.info(message)

def log_warning(message: str):
    """Log a warning message."""
    logging.warning(message)

def log_error(message: str):
    """Log an error message."""
    logging.error(message)
