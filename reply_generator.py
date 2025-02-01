import openai
import os
from dotenv import load_dotenv

# Set your OpenAI API key
load_dotenv()

# Get API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_ai_reply(email_snippet):
    """Generate an AI-powered reply to an email snippet."""
    prompt = f"Write a professional email response to the following message:\n\n{email_snippet}"

    response = openai.chat.completions.create(
        model="gpt-4",  # Or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are an AI email assistant that generates professional replies."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content