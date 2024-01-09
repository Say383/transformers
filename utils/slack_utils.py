import subprocess


def install_slack_sdk():
    subprocess.run(["pip", "install", "slack_sdk"])

def send_slack_notification(token, channel, message):
    from slack_sdk import WebClient

    client = WebClient(token=token)
    response = client.chat_postMessage(channel=channel, text=message)

    return response
