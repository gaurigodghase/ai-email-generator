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
        has_attachments = any(part.get("filename") for part in email_data["payload"].get("parts", []))
        

        email_data_list.append({
            "id": msg["id"],
            "name": headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No Subject"),
            "snippet": email_data.get("snippet", "No content available"),  # Short preview
            "body": body,  # Full email body
            "has attachments": has_attachments
        })

    return email_data_list

def get_email_body(payload):
    """Extracts the email body, handling nested structures and ignoring attachments."""
    
    def extract_text_from_parts(parts):
        """Recursively extract text from email parts, skipping attachments."""
        body_text = None
        body_html = None
        
        for part in parts:
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data", "")

            # Recursively handle nested parts (some emails store body within sub-parts)
            if "parts" in part:
                extracted_text = extract_text_from_parts(part["parts"])
                if extracted_text:
                    return extracted_text

            # Extract plain text body if available
            if mime_type == "text/plain" and body_data:
                body_text = decode_base64(body_data)

            # Extract HTML body if plain text is missing
            elif mime_type == "text/html" and body_data:
                body_html = decode_base64(body_data)

        return body_text or body_html  # Prefer text, fallback to HTML

    # Handle cases where the email has multiple parts
    if "parts" in payload:
        body_content = extract_text_from_parts(payload["parts"])
        if body_content:
            return body_content

    # Handle single-part emails
    if "body" in payload and payload["body"].get("data"):
        return decode_base64(payload["body"]["data"])

    return "No content available"  # If no body is found, return this message

def decode_base64(data):
    """Decode base64 encoded email content safely, handling decoding errors."""
    if not data:
        return "No content available"
    
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️ Base64 Decoding Error: {e}")
        return "No content available"
