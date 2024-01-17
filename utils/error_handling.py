import logging


def handle_api_request_error(error_message):
    """Handle API request errors"""
    logging.error(f"API request error: {error_message}")
    # Add specific error handling logic for API request errors


def handle_file_creation_error(file_path):
    """Handle file/directory creation errors"""
    logging.error(f"File/directory creation error: {file_path}")
    # Add specific error handling logic for file/directory creation errors


def handle_file_io_error(file_path, operation):
    """Handle file read/write errors"""
    logging.error(f"File I/O error: {file_path}, Operation: {operation}")
    # Add specific error handling logic for file read/write errors


def handle_exception(exception):
    """Handle general exceptions"""
    logging.exception("Unhandled exception occurred")
    # Add generic error handling logic for any unhandled exceptions


# Additional helper functions or classes can be added as needed
