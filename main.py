import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.services.gmail_service import process_and_respond_to_email

if __name__ == "__main__":
    process_and_respond_to_email()