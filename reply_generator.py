import openai
import os
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables (ensure OpenAI API Key is set)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def retrieve_relevant_attachment_content(query, email_has_attachments):
    """Retrieves relevant content from stored attachments using FAISS, only if the email has attachments."""
    
    # Skip FAISS retrieval if the current email has no attachments
    if not email_has_attachments:
        return "No attachment content found."

    embeddings = OpenAIEmbeddings()

    if not os.path.exists("attachments_index"):
        print("❌ No FAISS database found.")
        return "No attachment content found."

    vector_db = FAISS.load_local("attachments_index", embeddings, allow_dangerous_deserialization=True)
    results = vector_db.similarity_search(query, k=2)  # Retrieve top 2 relevant matches

    if not results:
        print("❌ No relevant attachment content found.")
        return "No attachment content found."

    retrieved_text = "\n\n".join([doc.page_content for doc in results])
    print("✅ Retrieved attachment content for query:", query)
    print(retrieved_text[:500])  # Print first 500 characters for debugging

    return retrieved_text

def generate_ai_reply(email_snippet, email_has_attachments):
    """Generate an AI-powered reply using RAG on attachments only if attachments exist."""
    relevant_attachment_content = retrieve_relevant_attachment_content(email_snippet, email_has_attachments)

    print("🔍 Debug: AI Reply Generation")
    print("✉️ Email Content:\n", email_snippet)
    print("📎 Attachment Content Retrieved:\n", relevant_attachment_content)

    # Construct the prompt for AI
    prompt = f"Write a professional email response to the following message:\n\nEmail Content: {email_snippet}"

    if relevant_attachment_content and relevant_attachment_content.strip() != "No attachment content found.":
        prompt += f"\n\nThe sender also included the following attachment content:\n{relevant_attachment_content}"

    print("📜 Final Prompt Sent to AI:\n", prompt[:1000])  # Print first 1000 chars of prompt for debugging

    # Generate AI response using OpenAI GPT
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI email assistant that references email attachments only if they exist."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def clear_faiss_storage():
    """Deletes the FAISS attachment index to prevent old attachments from being referenced."""
    if os.path.exists("attachments_index"):
        for file in os.listdir("attachments_index"):
            file_path = os.path.join("attachments_index", file)
            os.remove(file_path)
        os.rmdir("attachments_index")
        print("🗑️ FAISS storage cleared.")
    else:
        print("⚠️ No FAISS storage found to clear.")
