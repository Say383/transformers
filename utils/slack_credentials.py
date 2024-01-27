import os


def get_slack_api_token() -> str:
    return os.environ.get("SLACK_API_TOKEN", "")

def get_slack_channel_ids() -> List[str]:
    channel_ids = os.environ.get("SLACK_CHANNEL_IDS", "")
    return channel_ids.split(",") if channel_ids else []

SLACK_API_TOKEN = get_slack_api_token()
SLACK_CHANNEL_IDS = get_slack_channel_ids()
