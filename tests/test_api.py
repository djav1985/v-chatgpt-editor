from concurrent.futures import ThreadPoolExecutor
import os
import sys
from threading import Barrier
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from api import communicate_with_openai, get_client


class OpenAICommunicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = {
            "api_key": "test-api-key",
            "model": "gpt-5-mini",
            "max_concurrent_sections": 1,
            "organization": None,
            "project_id": None,
        }

    def test_sdk_exception_propagates_unchanged(self) -> None:
        api_error = RuntimeError("rate limit")
        with patch("api.get_client") as get_client:
            get_client.return_value.responses.create.side_effect = api_error

            with self.assertRaises(RuntimeError) as raised:
                communicate_with_openai("text", "system", "prefix", self.settings)

        self.assertIs(raised.exception, api_error)

    def test_uses_model_defaults_for_sampling(self) -> None:
        completion = Mock(output_text="corrected")
        with patch("api.get_client") as get_client:
            get_client.return_value.responses.create.return_value = completion

            result = communicate_with_openai("text", "system", "prefix", self.settings)

        self.assertEqual(result, "corrected")
        call_kwargs = get_client.return_value.responses.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gpt-5-mini")
        self.assertNotIn("temperature", call_kwargs)

    def test_uses_configured_model(self) -> None:
        completion = Mock(output_text="corrected")
        settings = {**self.settings, "model": "gpt-5"}
        with patch("api.get_client") as get_client:
            get_client.return_value.responses.create.return_value = completion

            communicate_with_openai("text", "system", "prefix", settings)

        self.assertEqual(
            get_client.return_value.responses.create.call_args.kwargs["model"],
            "gpt-5",
        )

    def test_rejects_response_without_message_content(self) -> None:
        completion = Mock(output_text="")
        with patch("api.get_client") as get_client:
            get_client.return_value.responses.create.return_value = completion

            with self.assertRaisesRegex(RuntimeError, "no message content"):
                communicate_with_openai("text", "system", "prefix", self.settings)

    def test_concurrent_client_initialization_creates_one_client(self) -> None:
        settings = {
            "api_key": "test-api-key",
            "model": "gpt-5-mini",
            "max_concurrent_sections": 1,
            "organization": None,
            "project_id": None,
        }
        barrier = Barrier(8)

        def initialize_client(_: int) -> object:
            barrier.wait()
            return get_client(settings)

        with patch("api._client", None), patch("api.OpenAI") as openai_client:
            with ThreadPoolExecutor(max_workers=8) as executor:
                clients = list(executor.map(initialize_client, range(8)))

        openai_client.assert_called_once_with(
            api_key="test-api-key", organization=None, project=None
        )
        self.assertTrue(all(client is clients[0] for client in clients))


if __name__ == "__main__":
    unittest.main()
