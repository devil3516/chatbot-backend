import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

def chat_with_groq(message):
    """Send a message to Groq API and return the AI response.

    Args:
        message (str): The user message to send to the AI.

    Returns:
        str: The AI's response message.
    """
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature = 0.3,
        max_tokens = 1000,
    )
    return response.choices[0].message.content.strip()

# """
# Groq API integration:
# - chat_with_groq(): Sends message to Groq API
# - Uses llama-3.3-70b model
# - Temperature and max_tokens configured
# - API key loaded from environment
# """