# api.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the secret OpenAI API key and other important configurations from the environment variables
# Default values are provided if those variables are not declared in the .env file
project_id = os.getenv("OPENAI_PROJECT_ID")
organization_id = os.getenv("OPENAI_ORG")
model = os.getenv("MODEL", "gpt-4o")
api_key = os.getenv("OPENAI_API_KEY")

# Validate that the API key is provided
if not api_key:
    raise ValueError("OPENAI_API_KEY is required but not found in environment variables")

# Instantiate the OpenAI API client with the given API key and configuration
client = OpenAI(
    api_key=api_key,
    organization=organization_id,
    project=project_id,
)


def communicate_with_openai(
    section_text, completed_sections, total_sections, system_message, user_prefix
):
    """Function to communicate with OpenAI API."""
    try:
        # Prepare the user message
        user_message = f"{user_prefix}: {section_text}"

        # Print the user message, completed and total sections
        print(
            f"\n\nSending to OpenAI API:\n\n{section_text}\n\nCompleted Sections: {completed_sections}/{total_sections}"
        )

        # Call the chat.completions API of OpenAI with essential parameters
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},  # System message
                {"role": "user", "content": user_message},  # User message
            ],
            max_tokens=3072,  # Maximum number of tokens in the generated message
            temperature=0.5,  # Adding temperature parameter
        )

        # Check if choices and message are available in the response
        if completion.choices and completion.choices[0].message:
            # Print only the content of the first message in choices
            print(f"API Response Content:\n{completion.choices[0].message.content}")
            return completion.choices[0].message.content
        else:
            raise Exception("Unexpected response format from OpenAI")

    except Exception as e:
        # If any error, raise it with proper information.
        raise Exception(f"Error communicating with OpenAI API: {e}")
