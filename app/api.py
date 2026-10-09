# api.py
from threading import Lock
from typing import Any

from openai import OpenAI

_client: OpenAI | None = None
_client_lock = Lock()


def get_client(settings: dict[str, Any]) -> OpenAI:
    """Return the shared OpenAI client, creating it on first use."""
    global _client
    with _client_lock:
        if _client is None:
            _client = OpenAI(
                api_key=settings["api_key"],
                organization=settings["organization"],
                project=settings["project_id"],
            )
        return _client


def communicate_with_openai(
    section_text: str,
    system_message: str,
    user_prefix: str,
    settings: dict[str, Any],
) -> str:
    """Function to communicate with OpenAI API."""
    user_message = f"{user_prefix}: {section_text}"
    response = get_client(settings).responses.create(
        model=settings["model"],
        instructions=system_message,
        input=user_message,
    )

    if not response.output_text:
        raise RuntimeError("OpenAI returned no message content.")
    return response.output_text
