import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not set in environment.")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(
    prompt: str,
    model: str = "gpt-4o",
    instructions: str = '',
) -> str:
    """
    """
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
    )
    return response.output_text
