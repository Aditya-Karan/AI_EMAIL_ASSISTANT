import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


# Define the required Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/userinfo.profile",  # ✅ required for name
    "https://www.googleapis.com/auth/contacts.readonly",  # optional for better sender info
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events"
]


def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth2.
    Handles token refresh and stores credentials in 'token.json'.
    """
    creds = None
    # Load existing credentials if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, perform OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds