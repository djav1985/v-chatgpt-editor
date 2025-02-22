import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Retrieve the secret OpenAI API key and other important configurations from the environment variables
# Default values are provided if those variables are not declared in the .env file
PROJECT_ID: Optional[str] = os.getenv("OPENAI_PROJECT_ID")
ORGANIZATION_ID: Optional[str] = os.getenv("OPENAI_ORG")
API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
MODEL: str = os.getenv("MODEL", "gpt-4o")

client: OpenAI = OpenAI(
    organization=ORGANIZATION_ID,
    project=PROJECT_ID,
    api_key=API_KEY,
)


def communicate_with_openai(
    section_text: str,
    completed_sections: int,
    total_sections: int,
    system_message: str,
    user_prefix: str,
) -> str:
    """
    Function to communicate with OpenAI API.

    Args:
        section_text (str): The text of the current section to be sent to the API.
        completed_sections (int): The number of sections completed so far.
        total_sections (int): The total number of sections.
        system_message (str): The system message to be sent to the API.
        user_prefix (str): The prefix to be added to the user message.

    Returns:
        str: The content of the response message from the OpenAI API.

    Raises:
        Exception: If there is an error communicating with the OpenAI API or if the response format is unexpected.
    """
    try:
        user_message: str = f"{user_prefix}: {section_text}"

        print(
            f"\n\nSending to OpenAI API:\n\n{section_text}\n\nCompleted Sections: {completed_sections}/{total_sections}"
        )

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=3072,
            temperature=0.5,
        )

        if completion.choices and completion.choices[0].message:
            print(f"API Response Content:\n{completion.choices[0].message.content}")
            return completion.choices[0].message.content
        else:
            raise Exception("Unexpected response format from OpenAI")

    except Exception as e:
        raise Exception(f"Error communicating with OpenAI API: {e}")
