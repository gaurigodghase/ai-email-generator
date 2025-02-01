from gmail_auth import authenticate_gmail
import base64

def fetch_recent_emails(max_results=20):
    """Fetch recent emails from the Gmail Primary category with snippet and full body."""
    service = authenticate_gmail()
    query = "category:primary"  # Fetch only Primary emails
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])

    email_data_list = []
    for msg in messages:
        email_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = {header["name"]: header["value"] for header in email_data["payload"]["headers"]}
        body = get_email_body(email_data["payload"])

        email_data_list.append({
            "id": msg["id"],
            "name": headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No Subject"),
            "snippet": email_data.get("snippet", "No content available"),  # Short preview
            "body": body  # Full email body
        })

    return email_data_list

def get_email_body(payload):
    """Extract the email body from the payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":  # Get plain text version
                return decode_base64(part["body"].get("data", ""))
            elif part["mimeType"] == "text/html":  # If plain text is not found, return HTML
                return decode_base64(part["body"].get("data", ""))
    elif "body" in payload:
        return decode_base64(payload["body"].get("data", ""))
    
    return "No content available"

def decode_base64(data):
    """Decode base64 encoded email content safely."""
    if not data:
        return "No content available"
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
