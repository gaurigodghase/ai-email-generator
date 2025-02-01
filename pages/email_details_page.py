import streamlit as st
from reply_generator import generate_ai_reply

def email_details_page():
    """Email details page with AI reply generation."""
    st.title("📩 Selected Email")

    # Get selected email from session state
    email = st.session_state.selected_email
    if not email:
        st.warning("⚠️ No email selected.")
        return

    # Display full email details
    st.markdown(f"**📨 From:** {email['name']}")
    st.markdown(f"**📌 Subject:** {email['subject']}")
    st.text_area("📜 Full Email Content", email["body"], height=300, disabled=True)

    # Generate AI response
    if "generated_reply" not in st.session_state or st.session_state.generated_reply is None:
        with st.spinner("Generating AI reply..."):
            ai_reply = generate_ai_reply(email["snippet"])
            st.session_state.generated_reply = ai_reply  # Save reply

    # Display AI-generated reply
    st.markdown("### 🤖 AI-Suggested Reply")
    st.text_area("📨 AI-Generated Reply", st.session_state.generated_reply, height=200, disabled=False)

    # Option to send the reply
    if st.button("📤 Send Reply"):
        st.success("✅ Reply sent successfully!")  # Add actual send functionality here

    # Back button to return to the inbox
    if st.button("⬅️ Back to Inbox"):
        st.session_state.selected_email = None
        st.session_state.generated_reply = None
        st.query_params
