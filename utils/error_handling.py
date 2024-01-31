import logging


def log_error(error_message):
    """
    Logs the given error message.
    """
    logging.error(error_message)

def handle_exception(exception):
    """
    Handles the given exception by logging the error message and providing an appropriate error response.
    """
    error_message = str(exception)
    log_error(error_message)
    # Add code to provide error response

def get_error_message(error_code):
    """
    Returns the error message corresponding to the given error code.
    """
    error_messages = {
        1: "Error message 1",
        2: "Error message 2",
        # Add more error messages as needed
    }
    return error_messages.get(error_code, "Unknown error")
