from email_fetcher import fetch_unread_emails
from reply_generator import generate_ai_reply

def main():
    """Main function to fetch emails and generate replies."""
    print("Starting AI Email Responder...\n")
    
    # Fetch unread emails
    unread_emails = fetch_unread_emails(max_results=5)
    if not unread_emails:
        print("✅ No emails to process.")
        return

    # Generate replies for each email
    for email in unread_emails:
        print(f"Original Email: {email['body']}")
        ai_reply = generate_ai_reply(email["snippet"])
        print(f"AI Reply: {ai_reply}\n")

if __name__ == "__main__":
    main()
