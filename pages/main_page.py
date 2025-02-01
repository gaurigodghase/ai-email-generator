import streamlit as st
from email_fetcher import fetch_recent_emails

def main_page():
    """Main page to display recent emails with Generate Reply button."""
    st.title("📧 AI Email Responder - Inbox")

    # Fetch recent emails from Gmail
    emails = fetch_recent_emails(max_results=20)
    if not emails:
        st.info("No recent emails found.")
        return

    # Display emails in a structured list
    for i, email in enumerate(emails):
        with st.container():
            st.markdown(f"**📨 From:** {email['name']}")
            st.markdown(f"**📌 Subject:** {email['subject']}")
            with st.expander("📜 View Email Preview",expanded=True):
                st.markdown(email["snippet"] + "...") # Unique key here

            if st.button(f"🤖 Generate Reply", key=f"generate_reply_{i}"):
                st.session_state.selected_email = email  # Save selected email
                st.session_state.generated_reply = None  # Reset previous reply
                st.query_params # Refresh the app

            st.divider()