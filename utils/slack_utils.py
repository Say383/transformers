from typing import Dict, List, Optional, Union

import requests
import slack_sdk
from slack_sdk import WebClient


def send_slack_message(message: str, token: str) -> bool:
    try:
        client = WebClient(token=token)
        response = client.chat_postMessage(channel="#general", text=message)
        if not response["ok"]:
            print("Failed to send message to Slack.")
            return False
        return True
    except slack_sdk.errors.SlackApiError as e:
        if e.response["error"] == "not_authed":
            print("Failed to send message to Slack: not_authed error.")
            return False
        else:
            raise e
