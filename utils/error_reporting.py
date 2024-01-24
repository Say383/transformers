import logging


def log_error(error_message: str) -> None:
    """
    Log the given error message to a file.
    """
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    logging.error(error_message)


def send_notification(error_message: str) -> None:
    """
    Send a notification with the given error message.
    """
    # Code to send a notification, e.g. via email or a messaging service
    # Replace this with the actual implementation
