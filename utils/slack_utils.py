# utils/slack_utils.py

from slack_sdk.errors import SlackApiError


def handle_authentication_error(error_message):
    """
    Handle authentication errors when sending messages to the Slack API.

    Args:
        error_message (str): The error message received from the Slack API.

    Returns:
        str: A meaningful error message to be displayed.
    """
    try:
        # Catch the specific exception raised when authentication fails
        raise SlackApiError(error_message)
    except SlackApiError as e:
        # Provide a user-friendly error message
        return f"Authentication error: {e.response['error']}"
