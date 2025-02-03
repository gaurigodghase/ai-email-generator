import os
import base64
import email
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import policy
from email.parser import BytesParser

def authenticate_gmail():
    """Authenticate and connect to Gmail API"""
    creds = Credentials.from_authorized_user_file('token.json')  # Ensure you have a valid token.json
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_emails(service, query='has:attachment'):  # Fetch emails with attachments
    """Retrieve emails matching a specific query"""
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    email_data = []
    for msg in messages[:10]:  # Limit to first 10 emails
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
        parsed_msg = BytesParser(policy=policy.default).parsebytes(msg_str.encode('utf-8'))

        # Ensure the email body is properly extracted
        body = ""
        if parsed_msg.is_multipart():
            for part in parsed_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break  # Extract only the first text/plain part
        else:
            body = parsed_msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        email_info = {
            'id': msg_id,
            'subject': parsed_msg['subject'],
            'from': parsed_msg['from'],
            'to': parsed_msg['to'],
            'date': parsed_msg['date'],
            'body': body,  # Ensure body is a string
            'attachments': []
        }
        
        # Process attachments safely
        for part in parsed_msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                file_data = part.get_payload(decode=True)
                
                # Convert attachment content to Base64 for JSON compatibility
                if file_data:
                    file_data_base64 = base64.b64encode(file_data).decode('utf-8')
                else:
                    file_data_base64 = ""

                email_info['attachments'].append({
                    'filename': filename,
                    'content': file_data_base64
                })
        
        email_data.append(email_info)
    
    return email_data

def save_email_data(email_data):
    """Save extracted email data as JSON"""
    with open('emails.json', 'w', encoding='utf-8') as f:
        json.dump(email_data, f, indent=4)

    print("Email data saved successfully!")

if __name__ == "__main__":
    service = authenticate_gmail()
    emails = get_emails(service)
    save_email_data(emails)
