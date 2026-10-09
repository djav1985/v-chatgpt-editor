from contextlib import redirect_stdout
from io import StringIO
import os
import tempfile
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

os.environ["OPENAI_API_KEY"] = "test-api-key"

from docx_handler import process_manuscript  # noqa: E402
from main import load_settings, workspace_for  # noqa: E402


class ConcurrencySettingTests(unittest.TestCase):
    def test_workspace_names_separate_edits_and_languages(self) -> None:
        self.assertEqual(workspace_for("book.docx"), os.path.join("tmp", "EDITED_book"))
        self.assertEqual(
            workspace_for("book.docx", "French"),
            os.path.join("tmp", "FRENCH_book"),
        )

    def test_defaults_to_one(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}, clear=True):
            settings = load_settings()
            self.assertEqual(settings["max_concurrent_sections"], 1)
            self.assertEqual(settings["model"], "gpt-5-mini")

    def test_reads_value(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-api-key", "MAX_CONCURRENT_SECTIONS": "3"},
            clear=True,
        ):
            self.assertEqual(load_settings()["max_concurrent_sections"], 3)

    def test_rejects_invalid_values(self) -> None:
        for bad in ("0", "-2", "many"):
            with patch.dict(
                os.environ,
                {"OPENAI_API_KEY": "test-api-key", "MAX_CONCURRENT_SECTIONS": bad},
                clear=True,
            ):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    load_settings()

    def test_rejects_missing_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY is not set"):
                load_settings()

    def test_rejects_empty_model(self) -> None:
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-api-key", "MODEL": "  "},
            clear=True,
        ):
            with self.assertRaisesRegex(ValueError, "MODEL must not be empty"):
                load_settings()


class ProcessManuscriptConcurrencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_directory = os.getcwd()
        os.chdir(self.temp_dir.name)
        self.section_dir = os.path.join("tmp", "EDITED_fixture")
        os.makedirs(self.section_dir)
        self.in_flight = 0
        self.max_in_flight = 0
        self.sent: list[str] = []
        self.lock = threading.Lock()

    def tearDown(self) -> None:
        os.chdir(self.original_directory)
        self.temp_dir.cleanup()

    def write_old_sections(self, count: int) -> None:
        for i in range(1, count + 1):
            path = os.path.join(self.section_dir, f"{i}-section.old")
            with open(path, "w", encoding="utf-8") as section_file:
                section_file.write(f"<p>section {i}</p>")

    def fake_api(
        self,
        section_text: str,
        system_message: str,
        user_prefix: str,
        settings: object | None = None,
    ) -> str:
        with self.lock:
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            self.sent.append(section_text)
        time.sleep(0.05)
        with self.lock:
            self.in_flight -= 1
        return section_text.upper()

    def run_process(self, concurrency: str) -> list[str]:
        settings = {
            "api_key": "test-api-key",
            "model": "gpt-5-mini",
            "max_concurrent_sections": int(concurrency),
            "organization": None,
            "project_id": None,
            "output_dir": "./output",
        }
        with patch(
            "docx_handler.communicate_with_openai", side_effect=self.fake_api
        ), patch("docx_handler.get_client"):
            return process_manuscript(
                "fixture.docx", "system", "prefix", settings, self.section_dir
            )

    def test_keeps_the_configured_number_in_flight(self) -> None:
        self.write_old_sections(8)

        result = self.run_process("3")

        self.assertEqual(self.max_in_flight, 3)
        self.assertEqual(result, [f"<P>SECTION {i}</P>" for i in range(1, 9)])

    def test_default_sends_one_at_a_time(self) -> None:
        self.write_old_sections(4)

        self.run_process("1")

        self.assertEqual(self.max_in_flight, 1)

    def test_logs_section_details_and_completion_progress(self) -> None:
        self.write_old_sections(3)
        output = StringIO()

        with redirect_stdout(output):
            self.run_process("1")

        output_lines = output.getvalue().splitlines()
        processing_lines = [
            line
            for line in output_lines
            if line.startswith("[process_manuscript] Processing section file:")
        ]
        self.assertEqual(len(processing_lines), 3)
        self.assertTrue(
            all(" | Text length: " in line for line in processing_lines)
        )

        progress_lines = [
            line
            for line in output_lines
            if line.startswith("[process_manuscript] Completed/Total Sections:")
        ]
        self.assertEqual(
            progress_lines,
            [
                "[process_manuscript] Completed/Total Sections: 1/3",
                "[process_manuscript] Completed/Total Sections: 2/3",
                "[process_manuscript] Completed/Total Sections: 3/3",
            ],
        )

    def test_resumes_without_resending_finished_sections(self) -> None:
        self.write_old_sections(3)
        done = os.path.join(self.section_dir, "2-section.new")
        with open(done, "w", encoding="utf-8") as new_file:
            new_file.write("already done")

        result = self.run_process("3")

        self.assertEqual(len(self.sent), 2)
        self.assertNotIn("<p>section 2</p>", self.sent)
        self.assertEqual(result[1], "already done")

    def test_failure_stops_new_sections_and_raises(self) -> None:
        self.write_old_sections(10)

        def failing_api(section_text: str, *args: object) -> str:
            if "section 1<" in section_text:
                raise ConnectionError("boom")
            return self.fake_api(section_text, "", "")

        settings = {
            "api_key": "test-api-key",
            "model": "gpt-5-mini",
            "max_concurrent_sections": 2,
            "organization": None,
            "project_id": None,
            "output_dir": "./output",
        }
        with patch(
            "docx_handler.communicate_with_openai", side_effect=failing_api
        ), patch("docx_handler.get_client"):
            with self.assertRaisesRegex(ConnectionError, "boom"):
                process_manuscript(
                    "fixture.docx", "system", "prefix", settings, self.section_dir
                )

        self.assertLess(len(self.sent), 9)


if __name__ == "__main__":
    unittest.main()
