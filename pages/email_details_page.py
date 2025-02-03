import streamlit as st
from reply_generator import generate_ai_reply
from email_fetcher import fetch_recent_emails
from gmail_auth import authenticate_gmail
import base64
from PyPDF2 import PdfReader
from docx import Document
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import os

def extract_attachments(email_id):
    """Fetch and extract attachments when a user selects an email."""
    service = authenticate_gmail()
    email_data = service.users().messages().get(userId="me", id=email_id, format="full").execute()

    attachments = []
    if "parts" in email_data["payload"]:
        for part in email_data["payload"]["parts"]:
            if part.get("filename"):
                attachment_id = part["body"].get("attachmentId")
                if attachment_id:
                    data = get_attachment(email_id, attachment_id, service)
                    extracted_text = extract_text_from_attachment(part["filename"], data)
                    attachments.append({"filename": part["filename"], "text": extracted_text, "raw_data": data})
    
    return attachments

def get_attachment(email_id, attachment_id, service):
    """Download and decode an attachment."""
    attachment = service.users().messages().attachments().get(
        userId="me", messageId=email_id, id=attachment_id
    ).execute()
    
    return base64.urlsafe_b64decode(attachment["data"])

def extract_text_from_attachment(filename, content):
    """Extract text from PDF, DOCX, and TXT attachments."""
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(content)
    elif filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")
    return "Unsupported file format."

def extract_text_from_pdf(content):
    """Extract text from a PDF file."""
    with open("temp.pdf", "wb") as f:
        f.write(content)
    
    reader = PdfReader("temp.pdf")
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    os.remove("temp.pdf")
    return text or "No readable text found."

def extract_text_from_docx(content):
    """Extract text from a DOCX file."""
    with open("temp.docx", "wb") as f:
        f.write(content)
    
    doc = Document("temp.docx")
    text = "\n".join([para.text for para in doc.paragraphs])
    os.remove("temp.docx")
    return text or "No readable text found."

def store_attachment_in_vector_db(attachments):
    """Stores extracted text from attachments in FAISS for retrieval."""
    embeddings = OpenAIEmbeddings()

    texts = []
    metadatas = []

    for attachment in attachments:
        if attachment["text"].strip():  # ✅ Store only non-empty attachments
            texts.append(attachment["text"])
            metadatas.append({"filename": attachment["filename"]})

    if not texts:
        print("⚠️ No valid attachment text found. Skipping FAISS storage.")
        return  # ✅ Exit early if no valid texts

    if os.path.exists("attachments_index"):
        vector_db = FAISS.load_local("attachments_index", embeddings, allow_dangerous_deserialization=True)
    else:
        vector_db = FAISS.from_texts(texts, embeddings)  # ✅ Ensure at least one valid embedding

    vector_db.add_texts(texts, metadatas=metadatas)
    vector_db.save_local("attachments_index")
    print(f"✅ Stored {len(texts)} attachments in FAISS!")

def email_details_page():
    """Automatically fetch email attachments, store them in FAISS, and display when requested."""
    st.title("📩 Selected Email")

    email = st.session_state.selected_email
    if not email:
        st.warning("⚠️ No email selected.")
        return

    st.markdown(f"**📨 From:** {email['name']}")
    st.markdown(f"**📌 Subject:** {email['subject']}")
    st.text_area("📜 Full Email Content", email.get("body", "No content available"), height=300, disabled=True)

    if "attachments" not in email:
        with st.spinner("🔄 Loading attachments..."):
            email["attachments"] = extract_attachments(email["id"])
            store_attachment_in_vector_db(email["attachments"])  
            st.session_state.selected_email = email  

    if email.get("attachments"):
        st.markdown("### 📎 Attachments")
        for attachment in email["attachments"]:
            with st.expander(f"📄 {attachment['filename']} (Click to view)"):
                st.text_area("Attachment Content", attachment["text"], height=400, disabled=True)

                st.download_button(
                    label=f"📥 Download {attachment['filename']}",
                    data=attachment["raw_data"],
                    file_name=attachment["filename"],
                    mime="application/octet-stream"
                )
    user_input = ""
    user_input = st.text_area("✏️ Optional: Add your thoughts or guidance for the AI reply", "")

    writing_style_pdf = st.file_uploader("📄 Upload a PDF with writing samples (optional)", type=["pdf"])
    writing_style_text = ""
    if writing_style_pdf:
        pdf_bytes = writing_style_pdf.read() 
        writing_style_text = extract_text_from_pdf(pdf_bytes)

    #Button to generate AI reply
    if st.button("🤖 Generate AI Reply"):
        with st.spinner("Generating AI reply..."):
            ai_reply = generate_ai_reply(email["snippet"], email["has attachments"], user_input, writing_style_text)  # ✅ Pass user input
            st.session_state.generated_reply = ai_reply

    #Display AI-generated reply only if available
    if "generated_reply" in st.session_state and st.session_state.generated_reply:
        st.markdown("### 🤖 AI-Suggested Reply")
        st.text_area("📨 AI-Generated Reply", st.session_state.generated_reply, height=200, disabled=False)

    #Back button to return to the inbox
    if st.button("⬅️ Back to Inbox"):
        st.session_state.selected_email = None
        st.session_state.generated_reply = None
