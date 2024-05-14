#main.py
import argparse
import os
from docx_handler import process_manuscript, merge_groups_and_save, split_into_sections


def main():
    # Initialize the manuscript editor and set up the command line arguments
    print("Initializing manuscript editor.")
    parser = argparse.ArgumentParser(
        description="Process a manuscript file in DOCX format."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set up the 'edit' command with an additional argument for sections
    edit_parser = subparsers.add_parser("edit", help="Edit a DOCX file")
    edit_parser.add_argument("filename", type=str, help="Path to the DOCX file")
    edit_parser.add_argument(
        "sections",
        type=int,
        help="Number of sections to split the manuscript into before editing",
    )

    # Set up the 'translate' command with an additional argument for sections
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

    # Parse the provided command line arguments
    args = parser.parse_args()

    # Check if the file exists for commands that require a file
    if args.command in ["edit", "translate"] and not os.path.exists(args.filename):
        print(f"Error: The file {args.filename} does not exist.")
        exit(1)

    if args.command == "edit":
        # Define user instructions for editing
        user_prefix = f"1. Review the text and output the corrected text based on your rules with no comments before or after:"
        system_message = f"You are a renowned contemporary romance book editor. Use the following rules to correct text: 1. Spelling, Grammar, and Punctuation Check: Thoroughly review the text for spelling errors, specifically converting UK English spellings to US English (e.g., 'colour' to 'color'). Correct any grammatical errors found in the text. Ensure punctuation is used correctly throughout the text. 2. Consistency and Correct Usage: Ensure verb tenses are used consistently and correctly throughout the text. Check for proper use of contractions (e.g., it's vs its) and correct any mistakes. Verify compound words and hyphenated words are used appropriately and consistently. Ensure consistent point of view and tense. 3. Dialogue and Inner Monologues: Focus exclusively on correcting spelling and punctuation in dialogues and inner monologues. Avoid making changes to the structure or wording of these sections, unless it's for punctuation or spelling. 4. Preserving Style and Meaning: Be cautious not to alter the original style or intended meaning of the text. Make edits sensitively to maintain the author's voice and tone. 5. Adjective Usage: Under no circumstance should you add or change adjectives except to correct the spelling. 6. Formatting and HTML Integrity: Keep all newlines and HTML formatting as is in the original text. Apply italics to internal monologue text using <i> and </i>. Mark sentences that have structural errors and need revision with <*> and </*>. 7. Final Output: Present the edited text without any comments or annotations before or after it. Ensure that the text is clean, with only the necessary corrections made."
        max_tokens = int("3072")
        section_size = int("256")
        action = f"EDIT"

        # Begin the editing process
        print(
            f"Editing {args.filename} after splitting into {args.sections} sections..."
        )
        sections = split_into_sections(args.filename, args.sections)
        print(f"{args.filename}: Split into {len(sections)} sections.")

        # Process each section (conceptual; adjust based on actual processing capabilities)
        corrected_manuscript = process_manuscript(
            args.filename, max_tokens, system_message, user_prefix
        )
        print("Manuscript editing completed.")

        # Build the final version of the edited manuscript
        print("Building the edited manuscript...")
        merge_groups_and_save(args.filename, action)
        print("Edited manuscript saved.")

    elif args.command == "translate":
        # Define user instructions for translation
        user_prefix = f"1. Translate the text from English to {args.language} based on your rules with no comments before or after:"
        system_message = f"You are a renowned expert in literary translation. Use the following rules to correct text: 1. Rather than adhering to a literal, word-for-word translation, deeply consider the distinct cultural nuances, structural and syntactical variations, grammatical norms, idiomatic expressions, and cultural contexts of each language. 2. Make appropriate adjustments to ensure these elements are accurately represented, while still preserving the original tone and intent of the text and maintaining the original HTML structure. 3. Don't wrap output in ```html ```"
        max_tokens = int("3072")
        section_size = int("1024")
        action = f"TRANSLATE"

        # Begin the translation process
        print(
            f"Translating {args.filename} into {args.language} after splitting into {args.sections} sections..."
        )
        sections = split_into_sections(args.filename, args.sections)
        print(f"{args.filename}: Split into {len(sections)} sections.")

        # Process each section (conceptual; adjust based on actual processing capabilities)
        corrected_manuscript = process_manuscript(
            args.filename, max_tokens, system_message, user_prefix
        )
        print("Manuscript translation completed.")

        # Build the final version of the edited manuscript
        print("Building the edited manuscript...")
        merge_groups_and_save(args.filename, action)
        print("Edited manuscript saved.")

    else:
        # Handle cases where no valid command is selected
        print("No valid command selected.")


# Entry point of the script
if __name__ == "__main__":
    main()
