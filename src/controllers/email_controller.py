import sys
import os
import base64
from googleapiclient.discovery import build

# Add the parent directory to the system path to allow imports from the src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the authentication function for Gmail
from src.authentication.gmail_auth import authenticate_gmail

def extract_email_body(payload):
    """
    Extracts the body text from the email payload.
    Supports both plain text and HTML emails.
    
    Args:
        payload (dict): The payload of the email, which contains the parts of the email (like body, attachments, etc.).
    
    Returns:
        str: The extracted body of the email, decoded from base64 and cleaned up.
    """
    body = ""
    
    # Check if the email has multiple parts (e.g., plain text and HTML)
    if "parts" in payload:
        # Loop through all parts and extract plain text if available
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":  # Only extract plain text part
                data = part["body"]["data"]  # Extract the base64-encoded data
                body = base64.urlsafe_b64decode(data).decode()  # Decode and convert to string
                break  

    # If the email doesn't have parts, it might be a simple single-body email
    elif "body" in payload:
        data = payload["body"]["data"]  # Extract the base64-encoded data from the body
        body = base64.urlsafe_b64decode(data).decode()  # Decode and convert to string
    
    return body.strip()  # Remove any leading/trailing whitespace from the body


def fetch_emails(max_results=1):
    """
    Fetches the latest emails from the user's Gmail inbox.
    Parses sender, subject, and email body.
    
    Args:
        max_results (int): The maximum number of emails to fetch (default is 1).
    
    Returns:
        list: A list of dictionaries containing email subject, sender, and body.
    """

    # Authenticate and get credentials for Gmail API
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)  # Build the Gmail service

    
    # Get a list of messages from the user's inbox
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])  # Get the messages from the response


    emails = []  
    # Loop through each message and extract relevant details
    for msg in messages:
        # Fetch the full message details using its ID
        email_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = email_data["payload"]  # Get the payload of the email (contains body and headers)
        headers = payload["headers"]  # Extract headers like sender and subject
        
        # Extract the subject and sender from headers
        subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
        sender = next((header["value"] for header in headers if header["name"] == "From"), "Unknown Sender")

        # Extract the email body using the helper function
        email_body = extract_email_body(payload)

        # Append the extracted details to the emails list
        emails.append({"subject": subject, "sender": sender, "body": email_body})

    return emails  

