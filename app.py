import streamlit as st
from pages.main_page import main_page
from pages.email_details_page import email_details_page

# Initialize session state
if "selected_email" not in st.session_state:
    st.session_state.selected_email = None
if "generated_reply" not in st.session_state:
    st.session_state.generated_reply = None

# Navigation logic
if st.session_state.selected_email:
    email_details_page()  # Navigate to email details page
else:
    main_page()  # Show the main page
