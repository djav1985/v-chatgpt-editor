# main.py
import argparse
import os
from docx_handler import process_manuscript, merge_groups_and_save, split_into_sections
from typing import List


def edit_command(filename: str, sections: int) -> None:
    """
    Edits a manuscript by splitting it into sections and processing each section for corrections.

    Args:
        filename (str): The name of the file to be edited.
        sections (int): The number of sections to split the manuscript into.

    Returns:
        None
    """
    user_prefix: str = (
        "Review and correct the following text with minimal changes. Output the corrected text with no comments before or after:"
    )
    system_message: str = (
        "As a renowned romance book editor, review and correct books with minimal changes. "
        "Focus on proper spelling, grammar, and punctuation while maintaining consistency in verb tenses, contractions, and compound words. "
        "Correct run-on sentences and ensure accurate punctuation in dialogues and inner monologues without altering their structure or wording. "
        "Preserve the author's voice and meaning. "
        "First, address spelling and typographical errors, followed by grammar and punctuation. "
        "Do not add or remove commas before the use of and. "
        "Ensure verb tense consistency throughout. "
        "Use <i> and </i> tags for inner monologue and long-form media titles, but not for emphasis. "
        "Only correct spelling in dialogues and inner monologues; avoid changing adjectives or expletives unless fixing a spelling error. "
        "Maintain all newlines and HTML formatting as in the original text, with minimal changes."
    )
    action: str = "EDIT"

    print(f"Editing {filename} after splitting into {sections} sections...")
    sections_list: List[str] = split_into_sections(filename, sections)
    print(f"{filename}: Split into {len(sections_list)} sections.")

    process_manuscript(filename, system_message, user_prefix)
    print("Manuscript editing completed.")

    print("Building the edited manuscript...")
    merge_groups_and_save(filename, action)
    print("Edited manuscript saved.")


def translate_command(filename: str, language: str, sections: int) -> None:
    """
    Translates the content of a given file into the specified language.

    Args:
        filename (str): The path to the file to be translated.
        language (str): The target language for translation.
        sections (int): The number of sections to split the file into for translation.

    Returns:
        None
    """
    user_prefix: str = (
        f"1. Translate the text from English to {language} based on your rules with no comments before or after:"
    )
    system_message: str = (
        "You are a renowned expert in literary translation. "
        "Use the following rules to correct text: "
        "1. Rather than adhering to a literal, word-for-word translation, deeply consider the distinct cultural nuances, structural and syntactical variations, grammatical norms, idiomatic expressions, and cultural contexts of each language. "
        "2. Make appropriate adjustments to ensure these elements are accurately represented, while still preserving the original tone and intent of the text and maintaining the original HTML structure. "
        "3. Don't wrap output in ```html ```"
    )
    action: str = language

    print(
        f"Translating {filename} into {language} after splitting into {sections} sections..."
    )
    sections_list: List[str] = split_into_sections(filename, sections)
    print(f"{filename}: Split into {len(sections_list)} sections.")

    process_manuscript(filename, system_message, user_prefix)
    print("Manuscript translation completed.")

    print("Building the edited manuscript...")
    merge_groups_and_save(filename, action)
    print("Translated manuscript saved.")


def build_command(filename: str) -> None:
    """
    Builds the final document for the given filename.

    This function initiates the build process for the specified file by
    merging groups and saving the final document. It prints messages to
    indicate the start and completion of the build process.

    Args:
        filename (str): The name of the file to be built.

    Returns:
        None
    """
    action: str = "BUILD"
    print(f"Building final document for {filename}...")
    merge_groups_and_save(filename, action)
    print(f"Final document {filename} built and saved.")


def main() -> None:
    """
    Main function to initialize the manuscript editor and set up command line arguments.

    Commands:
    - edit: Edit a DOCX file.
        Arguments:
            - filename: Path to the DOCX file.
            - sections: Number of sections to split the manuscript into before editing.
    - translate: Translate a DOCX file.
        Arguments:
            - filename: Path to the DOCX file.
            - language: Language to translate the manuscript into.
            - sections: Number of sections to split the manuscript into before translating.
    - build: Build a final DOCX from processed sections.
        Arguments:
            - filename: Path to the processed DOCX file.

    The function parses the provided command line arguments and calls the appropriate
    command function based on the selected command. It also checks if the specified
    file exists for commands that require a file.

    Raises:
        SystemExit: If the specified file does not exist for commands that require a file.
    """
    print("Initializing manuscript editor.")
    parser = argparse.ArgumentParser(
        description="Process a manuscript file in DOCX format."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    edit_parser = subparsers.add_parser("edit", help="Edit a DOCX file")
    edit_parser.add_argument("filename", type=str, help="Path to the DOCX file")
    edit_parser.add_argument(
        "sections",
        type=int,
        help="Number of sections to split the manuscript into before editing",
    )

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

    build_parser = subparsers.add_parser(
        "build", help="Build a final DOCX from processed sections"
    )
    build_parser.add_argument(
        "filename", type=str, help="Path to the processed DOCX file"
    )

    args = parser.parse_args()

    if args.command in ["edit", "translate", "build"] and not os.path.exists(
        args.filename
    ):
        print(f"Error: The file {args.filename} does not exist.")
        exit(1)

    if args.command == "edit":
        edit_command(args.filename, args.sections)
    elif args.command == "translate":
        translate_command(args.filename, args.language, args.sections)
    elif args.command == "build":
        build_command(args.filename)
    else:
        print("No valid command selected.")


if __name__ == "__main__":
    main()
