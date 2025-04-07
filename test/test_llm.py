import sys
import os

# Set the absolute path to the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from models.llm_service import generate_reply, extract_meeting_details

print("Starting the test script...")  # Debugging line


# Example email body for testing
email_body = """
Hello,

I would like to schedule a meeting with you next Monday, 10th April, at 2:30 PM to discuss the project updates.

Best regards,
Your colleague
"""

# Test the generate_reply function
print("Generated Reply:")
reply = generate_reply(email_body)
print(reply)

# Test the extract_meeting_details function
print("\nExtracted Meeting Details:")
meeting_details = extract_meeting_details(email_body)
print(meeting_details)
