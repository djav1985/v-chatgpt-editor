import os
import re
import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .api import generate_structured_report


def generate_report(filename):
    """
    Generate a report by iterating through all chapter files in the specified directory,
    submitting accumulated chapter content to the generate_structured_report function.
    Create individual JSON files for each chapter report.
    """
    try:
        file_base = os.path.splitext(os.path.basename(filename))[0]
        tmp_dir = f"./tmp/{file_base}"

        if not os.path.exists(tmp_dir):
            raise Exception(f"Directory {tmp_dir} does not exist.")

        chapter_files = sorted(
            [
                f
                for f in os.listdir(tmp_dir)
                if f.startswith("chapter") and f.endswith(".txt")
            ],
            key=lambda x: int(re.findall(r"\d+", x)[0]),
        )

        combined_content = ""

        for i, chapter_file in enumerate(chapter_files, start=1):
            chapter_path = os.path.join(tmp_dir, chapter_file)
            current_chapter = f"Chapter {i}"
            try:
                with open(chapter_path, "r") as file:
                    chapter_content = file.read()

                combined_content += chapter_content
                print(f"Preparing report for {current_chapter}...")

                chapter_report_path = os.path.join(tmp_dir, f"chapter{i}.json")

                if os.path.exists(chapter_report_path):
                    print(f"Report for {current_chapter} already exists. Skipping...")
                    continue

                chapter_report = generate_structured_report(
                    combined_content, current_chapter
                )

                with open(chapter_report_path, "w") as report_file:
                    json.dump(chapter_report.dict(), report_file, indent=4)

            except Exception as e:
                print(f"Error processing {current_chapter}: {e}")

    except Exception as e:
        print(f"An error occurred in generate_report: {e}")


def combine_json_reports(filename):
    """
    Combine individual chapter JSON files into a single consolidated JSON report.
    """
    try:
        file_base = os.path.splitext(os.path.basename(filename))[0]
        tmp_dir = f"./tmp/{file_base}"

        combined_report_filename = f"REPORT_{file_base}.json"
        combined_report_path = os.path.join(tmp_dir, combined_report_filename)

        report_data = {}

        if not os.path.exists(tmp_dir):
            raise Exception(f"Temporary directory {tmp_dir} does not exist.")

        # Use a custom sorting key to sort chapters numerically
        chapter_files = sorted(
            [f for f in os.listdir(tmp_dir) if f.startswith("chapter") and f.endswith(".json")],
            key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0
        )

        for file_name in chapter_files:
            chapter_path = os.path.join(tmp_dir, file_name)
            try:
                with open(chapter_path, "r") as chapter_file:
                    chapter_data = json.load(chapter_file)

                    # If ConsistencyInNarrativeElements or DetailConsistencyCheck are None, leave them as null
                    chapter_data["ConsistencyInNarrativeElements"] = chapter_data.get("ConsistencyInNarrativeElements", None)
                    chapter_data["DetailConsistencyCheck"] = chapter_data.get("DetailConsistencyCheck", None)

                    chapter_key = os.path.splitext(file_name)[0]
                    report_data[chapter_key] = chapter_data

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {file_name}: {e}")
            except Exception as e:
                print(f"Error reading file {file_name}: {e}")

        full_report = {f"Report For {file_base}": report_data}

        try:
            with open(combined_report_path, "w") as combined_file:
                json.dump(full_report, combined_file, indent=4)
            print(f"Combined report saved as {combined_report_path}")
        except Exception as e:
            print(f"Error saving combined report to {combined_report_path}: {e}")

    except Exception as e:
        print(f"An error occurred in combine_json_reports: {e}")
