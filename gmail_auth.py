import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the OAuth Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate with Gmail API and return the service instance."""
    creds = None

    # Load existing credentials if available
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no credentials or they are invalid, log in and save the token
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # Build the Gmail service
    service = build("gmail", "v1", credentials=creds)
    return service

# Test the authentication
if __name__ == "__main__":
    service = authenticate_gmail()
    print("✅ Gmail API authentication successful!")
