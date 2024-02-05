import logging
import os


def setup_logger(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger(os.path.join(os.path.dirname(__file__), "logs", "script.log"))

def log_message(message):
    logger.info(message)

def log_error(error):
    logger.error(error)

def set_log_file(log_file):
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.baseFilename = log_file
