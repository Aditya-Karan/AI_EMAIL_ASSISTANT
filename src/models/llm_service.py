import openai
import json
import os

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)


# Defining a funtion for genertaing reply using model api
def generate_reply(email_body):
    """
    Generate a summary and a polite response to an email using GPT-4.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant that summarizes emails and generates professional replies."},
            {"role": "user", "content": f"Summarize this email and generate a polite reply:\n\n{email_body}"}
        ],
        max_tokens=300
    )

    full_response = response.choices[0].message.content.strip()

    # Split summary and reply using a delimiter
    if "Reply:" in full_response:
        summary, reply = full_response.split("Reply:", 1)
        return summary.strip(), reply.strip()
    else:
        return "Summary not available", full_response
    


client = openai.OpenAI(api_key=api_key)  # Use env var in production!
def extract_meeting_details(email_text):
    """Use OpenAI LLM to extract meeting details from email text."""
    prompt = f"""
    Extract structured meeting details from the following email and in timezone field write Asia/Kolkata:

    "{email_text}"

    Output as JSON:
    {{
      "title": "<Meeting Title>",
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS",
      "timezone": "<TimeZone>"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts structured meeting data."},
            {"role": "user", "content": prompt}
        ],
    )

    content = response.choices[0].message.content

    # Optional: parse to dict (if you're confident the format is valid JSON)
    try:
         # Parse the JSON content
        meeting_details = json.loads(content)

        # Check for missing title and replace it with "Meeting" if needed
        if "title" in meeting_details and meeting_details["title"] == "<Meeting Title>":
            meeting_details["title"] = "Meeting"

        # Return the updated meeting details
        return meeting_details
    
    except json.JSONDecodeError:
        print("⚠️ Couldn't parse LLM response to JSON. Raw output returned.")
        return content
    