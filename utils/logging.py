import logging

# Configure logging settings
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="error.log",
    filemode="w"
)

def log_debug(message: str):
    """Log a debug-level message"""
    logging.debug(message)

def log_info(message: str):
    """Log an info-level message"""
    logging.info(message)

def log_warning(message: str):
    """Log a warning-level message"""
    logging.warning(message)

def log_error(message: str):
    """Log an error-level message"""
    logging.error(message)

def log_critical(message: str):
    """Log a critical-level message"""
    logging.critical(message)
