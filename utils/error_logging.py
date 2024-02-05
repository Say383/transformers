import logging


def log_error(error_message):
    """Log an error message."""
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(error_message)


def log_exception(exception):
    """Log an exception with detailed information."""
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.exception(exception)
