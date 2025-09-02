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

    # Set up the 'build' command
    build_parser = subparsers.add_parser(
        "build", help="Build a final DOCX from processed sections"
    )
    build_parser.add_argument(
        "filename", type=str, help="Path to the processed DOCX file"
    )

    # Parse the provided command line arguments
    args = parser.parse_args()

    try:
        # Check if the file exists for commands that require a file
        if args.command in ["edit", "translate", "build"] and not os.path.exists(
            args.filename
        ):
            print(f"Error: The file {args.filename} does not exist.")
            exit(1)

        if args.command == "edit":
            # Define user instructions for editing
            user_prefix = f"Review and correct the following text with minimal changes. Output the corrected text with no comments before or after:"
            system_message = f"As a renowned romance book editor, review and correct books with minimal changes. Focus on proper spelling, grammar, and punctuation while maintaining consistency in verb tenses, contractions, and compound words. Correct run-on sentences and ensure accurate punctuation in dialogues and inner monologues without altering their structure or wording. Preserve the author's voice and meaning. First, address spelling and typographical errors, followed by grammar and punctuation. Do not add or remove cammas before the use of and.  Ensure verb tense consistency throughout. Use <i> and </i> tags for inner monologue and long-form media titles, but not for emphasis. Only correct spelling in dialogues and inner monologues; avoid changing adjectives or expletives unless fixing a spelling error. Maintain all newlines and HTML formatting as in the original text, with minimal changes."
            action = "EDIT"

            # Begin the editing process
            print(
                f"Editing {args.filename} after splitting into {args.sections} sections..."
            )
            sections = split_into_sections(args.filename, args.sections)
            print(f"{args.filename}: Split into {len(sections)} sections.")

            # Process each section (conceptual; adjust based on actual processing capabilities)
            corrected_manuscript = process_manuscript(
                args.filename, system_message, user_prefix
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
            action = args.language

            # Begin the translation process
            print(
                f"Translating {args.filename} into {args.language} after splitting into {args.sections} sections..."
            )
            sections = split_into_sections(args.filename, args.sections)
            print(f"{args.filename}: Split into {len(sections)} sections.")

            # Process each section (conceptual; adjust based on actual processing capabilities)
            corrected_manuscript = process_manuscript(
                args.filename, system_message, user_prefix
            )
            print("Manuscript translation completed.")

            # Build the final version of the edited manuscript
            print("Building the edited manuscript...")
            merge_groups_and_save(args.filename, action)
            print("Translated manuscript saved.")

        elif args.command == "build":
            action = "BUILD"
            print(f"Building final document for {args.filename}...")
            merge_groups_and_save(args.filename, action)
            print(f"Final document {args.filename} built and saved.")

        else:
            print("No valid command selected.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
