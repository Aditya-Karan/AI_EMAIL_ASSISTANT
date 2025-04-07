import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """
    Authenticates and returns the Google Calendar API service.
    """
    creds = None
    # Check if token file exists and load the credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If credentials are invalid or expired, refresh or request new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh the expired token
        else:
            # Start OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    # Return the Calendar API service
    return build("calendar", "v3", credentials=creds)

def create_calender_event(event_details):
    """
    Creates a calendar event based on the provided event details.
    """
    # Debugging: Print the event details to ensure it's a dictionary and has the expected structure
    print("Event details:", event_details)
    
    # Check if event_details is a dictionary
    if not isinstance(event_details, dict):
        print("⚠️ Expected a dictionary, but received:", type(event_details))
        return  # Exit the function if event_details is not a dictionary
    
    # Check if necessary keys exist in event_details
    required_keys = ['date', 'time', 'title', 'timezone']
    for key in required_keys:
        if key not in event_details:
            print(f"⚠️ Missing key in event_details: {key}")
            return  # Exit the function if any key is missing
    
    # Get the authenticated calendar service
    service = get_calendar_service()

    # Parse the event start date and time from the event details
    start_dt = datetime.datetime.strptime(f"{event_details['date']} {event_details['time']}", "%Y-%m-%d %H:%M:%S")
    
    # Set the event end time (1 hour after the start time)
    end_dt = start_dt + datetime.timedelta(hours=1)

    # Define the event details for the Google Calendar API
    event = {
        "summary": event_details["title"],  # Event title
        "description": "Created by AI Assistant",  # Event description
        "start": {
            "dateTime": start_dt.isoformat(),  # Event start time
            "timeZone": event_details["timezone"],  # Time zone for the event
        },
        "end": {
            "dateTime": end_dt.isoformat(),  # Event end time
            "timeZone": event_details["timezone"],  # Time zone for the event
        },
    }

    # Insert the event into the calendar
    event_result = service.events().insert(calendarId="primary", body=event).execute()

    # Print success message and event details
    print("✅ Event created successfully.")
    print("📅 Summary:", event_result['summary'])
    print("🔗 Link:", event_result.get('htmlLink'))


