from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()

# Load from environment variable or store directly (secure way recommended)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_notification(subject, sender, body):
    """
    Sends a formatted Slack message with email info.
    """
    message = f":rotating_light: *URGENT EMAIL*\n*From:* {sender}\n*Subject:* {subject}\n\n{body[:1000]}"  # Truncate if too long

    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message
        )
        print("Slack message sent:", response["ts"])
    except SlackApiError as e:
        print("Slack API Error:", e.response["error"])
