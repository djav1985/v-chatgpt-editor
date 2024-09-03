import argparse
import os
import shutil
from docx_handler import (
    merge_groups_and_save,
    split_into_sections,
    split_into_chapters,
    json_report_to_docx,
)
from editor.process import process_manuscript
from editor.api import send_to_editor
from report.process import generate_report, combine_json_reports
from report.api import generate_structured_report


def main():
    # Initialize the manuscript editor and set up the command line arguments
    print("Initializing manuscript editor.")
    parser = argparse.ArgumentParser(
        description="Process a manuscript file in DOCX format."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set up the 'edit' command
    edit_parser = subparsers.add_parser("edit", help="Edit a DOCX file")
    edit_parser.add_argument("filename", type=str, help="Path to the DOCX file")
    edit_parser.add_argument(
        "sections",
        type=int,
        help="Number of sections to split the manuscript into before editing",
    )

    # Set up the 'translate' command
    translate_parser = subparsers.add_parser("translate", help="Translate a DOCX file")
    translate_parser.add_argument("filename", type=str, help="Path to the DOCX file")
    translate_parser.add_argument(
        "language", type=str, help="Language to translate the manuscript into"
    )
    translate_parser.add_argument(
        "sections",
        type=int,
        help="Number of sections to split the manuscript into before translating",
    )

    # Set up the 'report' command
    report_parser = subparsers.add_parser(
        "report", help="Generate a report for a DOCX file"
    )
    report_parser.add_argument("filename", type=str, help="Path to the DOCX file")

    # Parse the provided command line arguments
    args = parser.parse_args()

    # Check if the file exists for commands that require a file
    if args.command in ["edit", "translate", "report"] and not os.path.exists(
        args.filename
    ):
        print(f"Error: The file {args.filename} does not exist.")
        exit(1)

    if args.command == "edit":
        # Define user instructions for editing
        user_prefix = f"Review and correct the following text based on your rules output only the corrected text. Do not add any comments, info or explanations. Maintain all newlines, HTML and custom <center> </center>, <b> </b>, <i> </i> tags as in the original text. Complete you task with minimal changes to the text"
        system_message = (
            f"Review and correct user supplied text according to your following rules:"
            f"1 - Correct spelling, grammar, punctuations and run-on sentences."
            f"2 - Correct inconsistencies in verb tenses, contractions, and compound words."
            f"3 - Enclose all inner monologues inside <i> and </i>."
            f"4 - Enclose all sentences that require more than minimal changes in <*> and </*>."
            f"5 - Make sure to make as few changes to the original text as possible. Take no creative liberties"
            f"6 - Preserve the author's voice and meaning."
            f"7 - Avoid changing adjectives or expletives unless fixing a spelling error."
        )

        # Begin the editing process
        print(
            f"Editing {args.filename} after splitting into {args.sections} sections..."
        )
        sections = split_into_sections(args.filename, args.sections)
        print(f"{args.filename}: Split into {len(sections)} sections.")
        corrected_manuscript = process_manuscript(
            args.filename, system_message, user_prefix
        )
        print("Manuscript editing completed.")

        # Automatically build the final version after editing
        action = "EDIT"
        print("Building the edited manuscript...")
        merge_groups_and_save(args.filename, action)
        print("Edited manuscript saved.")

        # Remove the temporary directory and its contents
        file_base = os.path.splitext(os.path.basename(args.filename))[0]
        tmp_dir = f"./tmp/{file_base}"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            print(
                f"Temporary directory '{tmp_dir}' and its contents have been removed."
            )

    elif args.command == "translate":
        # Define user instructions for translation
        user_prefix = (
            f"1. Translate the text from English to {args.language} based on your rules"
        )
        system_message = (
            "Translate user supplied text according to the following rules:"
            "1 - Rather than adhering to a literal, word-for-word translation, deeply consider the distinct cultural nuances, structural and syntactical variations, grammatical norms, idiomatic expressions, and cultural contexts of each language."
            "2 - Make appropriate adjustments to ensure these elements are accurately represented, while still preserving the original tone and intent of the text."
            "3 - Where appropriate for style and context you may keep the English version of a word."
            "4 - Your output should keep current newlines and HTML formatting."
            "5 - Your output should not include any comments before or after the translated text."
        )
        action = args.language

        # Begin the translation process
        print(
            f"Translating {args.filename} into {args.language} after splitting into {args.sections} sections..."
        )
        sections = split_into_sections(args.filename, args.sections)
        print(f"{args.filename}: Split into {len(sections)} sections.")
        corrected_manuscript = process_manuscript(
            args.filename, system_message, user_prefix
        )
        print("Manuscript translation completed.")

        # Automatically build the final version after translation
        print("Building the translated manuscript...")
        merge_groups_and_save(args.filename, action)
        print("Translated manuscript saved.")

        # Remove the temporary directory and its contents
        file_base = os.path.splitext(os.path.basename(args.filename))[0]
        tmp_dir = f"./tmp/{file_base}"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            print(
                f"Temporary directory '{tmp_dir}' and its contents have been removed."
            )

    elif args.command == "report":
        print(f"Splitting {args.filename} into chapters...")
        split_into_chapters(args.filename)
        print(f"Generating report for {args.filename}...")
        generate_report(args.filename)
        combine_json_reports(args.filename)
        json_report_to_docx(args.filename)
        print("Report saved.")

    else:
        print("No valid command selected.")


if __name__ == "__main__":
    main()
