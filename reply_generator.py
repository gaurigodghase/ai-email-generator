import openai
import os
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# Load environment variables (ensure OpenAI API Key is set)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_digital_twin(style_text):
    """
    Uses an AI agent to extract a person's unique writing style (Digital Twin Persona).
    """
    llm = ChatOpenAI(model_name="gpt-4")

    def extract_style(text):
        """AI Agent to analyze the writing style from the provided text."""
        response = llm.invoke(f"""
        You are an AI writing style expert.
        Analyze the following text and extract key patterns that define the writer’s style.

        - **Sentence structure** (short, long, structured, informal)
        - **Phrasing patterns** (e.g., repetitive phrases, rhetorical questions)
        - **Word choices** (formal, casual, humorous, technical, archaic)
        - **Tone & speech quirks** (pirate-like, old-English, overly polite, blunt)
        - **Punctuation & grammar** (Oxford comma, ellipses, dashes, emojis)
        - **Preferred opening & closing phrases**

        TEXT:
        {text}

        Respond with a structured summary of the writer’s unique style.
        """)
        return response

    style_tool = Tool(
        name="DigitalTwinGenerator",
        func=extract_style,
        description="Extracts a person's writing style from provided text."
    )

    agent = initialize_agent(
        tools=[style_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    extracted_style = agent.run(f"Analyze and extract the writing style of this person: {style_text}")
    return extracted_style



def retrieve_relevant_attachment_content(query, email_has_attachments):
    """Retrieves relevant content from stored attachments using FAISS, only if the email has attachments."""
    if not email_has_attachments:
        return "No attachment content found."

    embeddings = OpenAIEmbeddings()

    if not os.path.exists("attachments_index"):
        print("❌ No FAISS database found.")
        return "No attachment content found."

    vector_db = FAISS.load_local("attachments_index", embeddings, allow_dangerous_deserialization=True)
    results = vector_db.similarity_search(query, k=5)  # Retrieve top 2 relevant matches

    if not results:
        print("❌ No relevant attachment content found.")
        return "No attachment content found."

    retrieved_text = "\n\n".join([doc.page_content for doc in results])
    print("✅ Retrieved attachment content for query:", query)
    print(retrieved_text[:500])  # Print first 500 characters for debugging

    return retrieved_text

def generate_draft_email(email_snippet, email_has_attachments, user_input, writing_style):
    """Uses an AI agent to generate a draft email reply using relevant attachment content if available."""
    
    relevant_attachment_content = retrieve_relevant_attachment_content(email_snippet, email_has_attachments)

    def generate_response(text):
        """AI Agent to generate the draft email response based on provided context."""
        llm = ChatOpenAI(model_name="gpt-4")
        prompt = f"Write an email response to the following message:\n\nEmail Content: {text}"

        if relevant_attachment_content and relevant_attachment_content.strip() != "No attachment content found.":
            prompt += f"\n\nThe sender also included the following attachment content:\n{relevant_attachment_content}"
        
        if user_input.strip():  # ✅ Include user input if provided
            prompt += f"\n\nAdditionally, the following perspective should be considered:\n{user_input}"

        if writing_style and writing_style.strip() != "No writing style provided.":
            prompt += f"\n\nThe response should be written in a manner that mirrors the following writing style:\n\n{writing_style}\n\nEnsure that the response adopts the tone, structure, and phrasing of the provided style, making it a digital twin of the given writing style."

        prompt += f"Generate a clear and contextually relevant reply."
        response = llm.invoke(prompt)
        return response

    response_tool = Tool(
        name="EmailResponseGenerator",
        func=generate_response,
        description="Generates a draft email response considering the email content, attachments, and user input."
    )

    agent = initialize_agent(
        tools=[response_tool],
        llm=ChatOpenAI(model_name="gpt-4"),
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    response = agent.run(f"Generate an email response for this email: {email_snippet}")
    return response


def generate_ai_reply(email_snippet, email_has_attachments, user_input, style_sample_text):
    """
    Multi-agent pipeline for AI email response generation:
    """
    if style_sample_text.strip():
        extracted_style = generate_digital_twin(style_sample_text)
    else:
        extracted_style = "No writing style provided."

    response = generate_draft_email(email_snippet, email_has_attachments, user_input, extracted_style)
    print("\n✅ AI-Generated Styled Response:")
    print(response)

    return response


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
