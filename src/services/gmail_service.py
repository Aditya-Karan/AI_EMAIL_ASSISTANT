# importing libraries and functions

import os
import sys
import base64
from googleapiclient.discovery import build
from email.utils import parseaddr
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.models.llm_service import generate_reply, extract_meeting_details
from src.db.database import init_db, store_emails  #
from src.utils.slack_notifier import send_slack_notification
from src.utils.calender_api import create_calender_event
from src.utils.web_search import search_web
from src.authentication.gmail_auth import authenticate_gmail
from src.controllers.email_controller import fetch_emails


def is_simple_case(email_body):
    """
    Determine if the email is a simple case that can be auto-replied to.
    For example, simple confirmations or brief emails like 'thank you'.
    
    Args:
    email_body (str): The body text of the email to analyze.
    
    Returns:
    bool: True if the email body contains certain simple keywords, False otherwise.
    """
    
    # List of keywords typically found in simple emails (like confirmations or acknowledgements)
    simple_keywords = ["thank you", "confirmation", "acknowledged", "received"]
    
    # Iterate over the keywords and check if any of them appear in the email body (case-insensitive)
    for keyword in simple_keywords:
        if keyword.lower() in email_body.lower():
            # If a keyword is found, return True indicating it's a simple case
            return True
    
    # If none of the keywords are found, return False indicating it's not a simple case
    return False



def get_gmail_user_name(creds):
    """
    Fetch the Gmail user's name using the People API.
    """
    try:
        people_service = build("people", "v1", credentials=creds)
        profile = people_service.people().get(resourceName='people/me', personFields='names').execute()
        names = profile.get("names", [])
        if names:
            return names[0].get("displayName", "Your Name")
    except Exception as e:
        print(f"Error fetching user name: {e}")
    return "Your Name"


def personalize_reply(reply_text, sender_name, user_name):
    """
    Replace placeholders with actual names and ensure signature is at the very end.
    """
    # Replace "Dear ..." with "Dear <sender_name>,"
    reply_text = re.sub(r"Dear\s+.*?,", f"Dear {sender_name},", reply_text)

    # Remove brackets around placeholder names
    reply_text = re.sub(r"\[([^\]]+)\]", r"\1", reply_text)

    # Remove any existing signature like 'Best Regards,...'
    reply_text = re.sub(r"(Best\s+Regards,?.*?$)", "", reply_text, flags=re.IGNORECASE | re.DOTALL)

    # Strip trailing whitespace and add a clean signature at the very end
    reply_text = reply_text.strip() + f"\n\nBest Regards,\n{user_name}"

    return reply_text


def insert_web_snippet_before_signature(reply, web_snippet):
    """
    Inserts the web snippet into the reply before the final signature lines.
    Ensures only one blank line between reply and web snippet, and one before the signature.
    """
    if not web_snippet:
        return reply  # If no web search, return the reply as is

    lines = reply.strip().split("\n")

    # Find where the signature starts
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().lower() in ["best regards,", "thanks,"]:
            signature_index = i
            break
    else:
        # If no signature is found, just append web snippet with correct spacing
        return reply.rstrip() + f"\n\nAdditionally, based on the latest information from the web, here are some insights:\n{web_snippet}"

    # Extract reply body and signature separately
    body = "\n".join(lines[:signature_index]).rstrip()  # Remove extra trailing spaces/newlines
    signature = "\n".join(lines[signature_index:])  # Keep signature as is

    # Return properly formatted response with exactly one blank line before each section
    return f"{body}\n\nAdditionally, based on the latest information from the web, here are some insights:\n{web_snippet}\n\n{signature}"



def process_email_for_web_search(email_body):
    """
    Analyze the email body and trigger a web search if it contains question-related keywords.
    """
    question_keywords = ["what is", "how to", "explain", "define", "current", "latest"]
    
    # Trigger web search if any question-related keyword is found
    if any(keyword in email_body.lower() for keyword in question_keywords):
        print("[Web Search Triggered]")
        return search_web(email_body)
    
    return None
    


def is_urgent_email(email_body, subject):
    """
    Check if the email is urgent based on certain keywords in the subject and body.
    """
    urgency_keywords = [
        "urgent", "asap", "immediately", "important", "emergency", 
        "action required", "respond quickly", "critical", "deadline", "attention"
    ]
    
    # Combine subject and body to check for urgency keywords
    combined = (subject + " " + email_body).lower()
    
    return any(keyword in combined for keyword in urgency_keywords)


def mark_meeting_details(meeting_details):
    # print('outside')
    try:
        print(type(meeting_details))
        # print(meeting_details.len())
        if type(meeting_details)==str or type(meeting_details)==dict:
            # print('kk')
            meeting_details=[meeting_details]

        # print(meeting_details)
        
        for event in meeting_details:
            #print(event)
            create_calender_event(event)
    except Exception as e:
        print(f"⚠️ Could not create calendar event: {e}")


def process_and_respond_to_email():
    """
    Process the email content, summarize, extract meeting details, and generate a draft reply.
    Also, ensure safeguards to auto-send or ask for confirmation before replying.
    """
    # Fetch the latest emails
    emails = fetch_emails()

    for email in emails:
        print(f"Processing email: {email['subject']} from {email['sender']}")

        raw_email = parseaddr(email["sender"])
        sender_name = raw_email[0] if raw_email[0] else raw_email[1].split("@")[0].capitalize()

        user_name = get_gmail_user_name(authenticate_gmail())

        # Generate a summary and a reply using LLM
        summary, reply = generate_reply(email['body'])
        reply = personalize_reply(reply, sender_name, user_name)
        reply = reply.replace("Your Name", user_name)

        # Trigger web search for additional context or data
        web_snippet = process_email_for_web_search(email['body'])

        reply = insert_web_snippet_before_signature(reply, web_snippet)

        # Print the summary and generated reply only once for debugging
        print(f"Summary: {summary}")
        print(f"Generated reply: {reply}")

        # Extract meeting details if any
        meeting_details = extract_meeting_details(email['body'])
        print(f"Meeting Details: {meeting_details}")


        # checking urgent mail or not
        if is_urgent_email(email['body'], email['subject']):
            print("Urgent email detected. Sending Slack notification...")
            send_slack_notification(email['subject'], email['sender'], email['body'])

        # Store emails in the database
        store_emails([email])


        # Check if the email is simple and can be auto-replied
        if is_simple_case(email['body']):
            print("This is a simple email, auto-replying...")
            send_reply_via_gmail(reply, email)  # Send the reply automatically

            if meeting_details:
                mark_meeting_details(meeting_details)

        else:
            print("This is a complex email, logging and asking for confirmation...")

            # Log email for manual review
            log_email_for_confirmation(email['subject'], email['sender'], email['body'], reply)

            # Ask user for confirmation before sending
            confirmation=ask_for_user_confirmation(reply, email)

            if confirmation == 'y':
                if meeting_details:
                    mark_meeting_details(meeting_details)


def log_email_for_confirmation(subject, sender, body, reply):
    """
    Logs the email for manual review before sending a reply.
    """
    print(f"\n[LOGGING] Email from {sender} with subject '{subject}'")

def ask_for_user_confirmation(reply,email):
    """
    Asks the user for confirmation before sending the reply.
    """
    confirmation = input(f"Do you want to send the following reply? (y/n): ")
    if confirmation.lower() == 'y':
        send_reply_via_gmail(reply,email)
        print("Reply sent!")
    else:
        print("Reply not sent.")

    return confirmation.lower()
        

def send_reply_via_gmail(reply, email):
    """
    Sends the reply via Gmail API, using the provided email details and reply text.
    """
    creds = authenticate_gmail()  # Authenticate and get credentials
    service = build("gmail", "v1", credentials=creds)  # Build the Gmail service

    # Create the message to send (using the email's sender and subject)
    message = create_message("me", email['sender'], "Re: " + email['subject'], reply)
    
    # Send the message
    send_message(service, "me", message)


def create_message(sender, to, subject, body):
    """
    Creates a message to send via Gmail API by composing a MIME message.
    """
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Create the email structure
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    
    # Attach the email body
    msg = MIMEText(body)
    message.attach(msg)
    
    # Encode the message in base64 format for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}

def send_message(service, sender, message):
    """
    Sends an email message via the Gmail API.
    """
    try:
        # Send the email using Gmail API
        message = service.users().messages().send(userId=sender, body=message).execute()
        print(f"Message sent! Message ID: {message['id']}")
    except Exception as error:
        # Handle any errors that occur during sending
        print(f"An error occurred: {error}")
