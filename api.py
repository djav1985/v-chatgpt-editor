# api.py

# Required libraries are imported
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the secret OpenAI API key and other important configurations from the environment variables
# Default values are provided if those variables are not declared in the .env file
api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('MODEL', 'gpt-4-1106-preview')
user_prefix = os.getenv('USER_PREFIX', '')
system_message = os.getenv('SYSTEM_MESSAGE', '')
max_tokens = int(os.getenv('MAX_TOKENS', 4096))

# Instantiate the OpenAI API client with the given API key
client = OpenAI(api_key=api_key)

def communicate_with_openai(section_text, completed_sections, total_sections):
    """Function to communicate with OpenAI API."""
    try:
        # Prepare the user message
        user_message = f"{user_prefix}: {section_text}"

        # Print the user message, completed and total sections
        print(f"\nSending to OpenAI API: User Message: {user_message}\nCompleted Sections: {completed_sections} | Total Sections: {total_sections}")

        # Call the chat.completions API of OpenAI with essential parameters
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},  # System message
                {"role": "user", "content": user_message}  # User message
            ],
            max_tokens=max_tokens)  # Maximum number of tokens in the generated message

        print(f"Entire API Response:\n{completion}")

        # Check if choices and message are available in the response
        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content
        else:
            raise Exception("Unexpected response format from OpenAI")

    except Exception as e:
        # If any error, raise it with proper information.
        raise Exception(f"Error communicating with OpenAI API: {e}")
