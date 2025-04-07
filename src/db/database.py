import sqlite3
import os

# Database file path, stored in the same directory as the script
DB_PATH = os.path.join(os.path.dirname(__file__), "emails.db")

def init_db():
    """
    Initializes the SQLite database and creates a table for storing emails.
    If the table already exists, it won't be created again.
    """
    conn = sqlite3.connect(DB_PATH)  # Connect to the SQLite database (it will create the file if it doesn't exist)
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    
    # Create the 'emails' table if it doesn't exist
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  # Auto-increment primary key
            sender TEXT,  # Sender of the email
            subject TEXT,  # Subject of the email
            body TEXT  # Body content of the email
        )
    ''')
    
    conn.commit()  # Commit changes (save the table structure)
    conn.close()  # Close the database connection

def store_emails(emails):
    """
    Stores a list of emails in the database.
    
    :param emails: List of dictionaries with 'sender', 'subject', and 'body' keys.
    Each dictionary represents an email.
    """
    conn = sqlite3.connect(DB_PATH)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to interact with the database
    
    # Iterate over the list of emails and insert each email into the database
    for email in emails:
        cursor.execute('''
            INSERT INTO emails (sender, subject, body) 
            VALUES (?, ?, ?)
        ''', (email["sender"], email["subject"], email["body"]))

    
    conn.commit()  # Commit changes (save the emails into the database)
    conn.close()  # Close the database connection
