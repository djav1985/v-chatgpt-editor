from functools import lru_cache

import tiktoken


@lru_cache(maxsize=8)
def _encoding_for_model(model_name: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError as exc:
        raise ValueError(
            f"Token counting is not configured for model '{model_name}'. "
            "Use a model recognized by the installed tiktoken version."
        ) from exc


def count_model_tokens(text: str, model_name: str = "gpt-5-mini") -> int:
    """Count serialized text tokens using the supplied model's encoding."""
    return len(_encoding_for_model(model_name).encode(text))
