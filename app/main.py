import argparse
import os
import re
import sys
from typing import Any

from dotenv import load_dotenv

from docx_handler import process_manuscript, merge_groups_and_save, split_into_sections
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    RateLimitError,
)


def load_settings(require_api: bool = True) -> dict[str, Any]:
    """Load environment settings and validate those needed for this command."""
    load_dotenv()
    settings: dict[str, Any] = {
        "output_dir": os.getenv("OUTPUT_DIR", "./output"),
    }

    if not require_api:
        return settings

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None or not api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY is not set. Add it to the environment or the .env file."
        )

    model = os.getenv("MODEL", "gpt-5-mini")
    if not model.strip():
        raise ValueError("MODEL must not be empty.")

    raw_concurrency = os.getenv("MAX_CONCURRENT_SECTIONS", "1")
    try:
        max_concurrent_sections = int(raw_concurrency)
    except ValueError:
        max_concurrent_sections = 0
    if max_concurrent_sections < 1:
        raise ValueError(
            "MAX_CONCURRENT_SECTIONS must be a positive integer, "
            f"got '{raw_concurrency}'."
        )

    settings.update(
        {
            "api_key": api_key.strip(),
            "model": model.strip(),
            "max_concurrent_sections": max_concurrent_sections,
            "organization": os.getenv("OPENAI_ORG"),
            "project_id": os.getenv("OPENAI_PROJECT_ID"),
        }
    )
    return settings


def workspace_for(filename: str, language: str | None = None) -> str:
    """Build an isolated temporary workspace for editing or one translation."""
    source = os.path.splitext(os.path.basename(filename))[0]
    if language is None:
        prefix = "EDITED"
    else:
        language_prefix = re.sub(r"[^A-Za-z0-9_-]+", "_", language.strip())
        language_prefix = language_prefix.strip("_").upper()
        if not language_prefix:
            raise ValueError("The translation language must not be empty.")
        prefix = language_prefix
    return os.path.join("tmp", f"{prefix}_{source}")


def main() -> None:
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
        "max_tokens",
        type=int,
        help=(
            "Maximum model tokens per section of serialized manuscript text; "
            "an oversized paragraph is kept intact"
        ),
    )

    # Set up the 'translate' command
    translate_parser = subparsers.add_parser(
        "translate", help="Translate a DOCX file"
    )
    translate_parser.add_argument("filename", type=str, help="Path to the DOCX file")
    translate_parser.add_argument(
        "language", type=str, help="Language to translate the manuscript into"
    )
    translate_parser.add_argument(
        "max_tokens",
        type=int,
        help=(
            "Maximum model tokens per section of serialized manuscript text; "
            "an oversized paragraph is kept intact"
        ),
    )

    # Set up the 'build' command
    build_parser = subparsers.add_parser(
        "build", help="Build a final DOCX from processed sections"
    )
    build_parser.add_argument(
        "filename", type=str, help="Path to the processed DOCX file"
    )
    build_mode = build_parser.add_mutually_exclusive_group(required=True)
    build_mode.add_argument(
        "--edited", action="store_true", help="Rebuild the edited document"
    )
    build_mode.add_argument(
        "--language", type=str, help="Rebuild a translation for this language"
    )

    # Parse the provided command line arguments
    args = parser.parse_args()

    try:
        # Check if the file exists for commands that require a file
        if args.command in ["edit", "translate", "build"] and not os.path.exists(
            args.filename
        ):
            print(f"Error: The file {args.filename} does not exist.", file=sys.stderr)
            sys.exit(1)

        if args.command == "edit":
            settings = load_settings()
            tmp_dir = workspace_for(args.filename)
            # Define user instructions for editing
            user_prefix = (
                "Review and correct the following text with minimal changes. "
                "Output the corrected text with no comments before or after:"
            )
            system_message = (
                "As a renowned romance book editor, review and correct books with "
                "minimal changes. Focus on proper spelling, grammar, and "
                "punctuation while maintaining consistency in verb tenses, "
                "contractions, and compound words. Correct run-on sentences and "
                "ensure accurate punctuation in dialogues and inner monologues "
                "without altering their structure or wording. Preserve the "
                "author's voice and meaning. First, address spelling and "
                "typographical errors, followed by grammar and punctuation. Do "
                "not add or remove cammas before the use of and.  Ensure verb "
                "tense consistency throughout. Use <i> and </i> tags for inner "
                "monologue and long-form media titles, but not for emphasis. "
                "Only correct spelling in dialogues and inner monologues; avoid "
                "changing adjectives or expletives unless fixing a spelling "
                "error. Maintain all newlines and HTML formatting as in the "
                "original text, with minimal changes. Lines of the form "
                "<image NAME POSITION> must be copied exactly, never altered, "
                "removed, or moved."
            )
            action = "EDIT"

            # Begin the editing process
            print(
                f"Editing {args.filename} with a "
                f"{args.max_tokens}-token section budget..."
            )
            sections = split_into_sections(
                args.filename,
                args.max_tokens,
                cache_key=f"{action}\n{system_message}\n{user_prefix}",
                model_name=settings["model"],
                tmp_dir=tmp_dir,
            )
            print(f"{args.filename}: Split into {len(sections)} sections.")

            # Process each section
            process_manuscript(
                args.filename, system_message, user_prefix, settings, tmp_dir
            )
            print("Manuscript editing completed.")

            # Build the final version of the edited manuscript
            print("Building the edited manuscript...")
            merge_groups_and_save(
                args.filename, action, settings["output_dir"], tmp_dir
            )
            print("Edited manuscript saved.")

        elif args.command == "translate":
            settings = load_settings()
            tmp_dir = workspace_for(args.filename, args.language)
            # Define user instructions for translation
            user_prefix = (
                f"1. Translate the text from English to {args.language} based on "
                "your rules with no comments before or after:"
            )
            system_message = (
                "You are a renowned expert in literary translation. Use the "
                "following rules to correct text: 1. Rather than adhering to a "
                "literal, word-for-word translation, deeply consider the "
                "distinct cultural nuances, structural and syntactical "
                "variations, grammatical norms, idiomatic expressions, and "
                "cultural contexts of each language. 2. Make appropriate "
                "adjustments to ensure these elements are accurately "
                "represented, while still preserving the original tone and "
                "intent of the text and maintaining the original HTML "
                "structure. 3. Don't wrap output in ```html ```. 4. Copy lines "
                "of the form <image NAME POSITION> exactly, never altering, "
                "removing, or moving them."
            )
            action = args.language

            # Begin the translation process
            print(
                f"Translating {args.filename} into {args.language} with a "
                f"{args.max_tokens}-token section budget..."
            )
            sections = split_into_sections(
                args.filename,
                args.max_tokens,
                cache_key=f"{action}\n{system_message}\n{user_prefix}",
                model_name=settings["model"],
                tmp_dir=tmp_dir,
            )
            print(f"{args.filename}: Split into {len(sections)} sections.")

            # Process each section
            process_manuscript(
                args.filename, system_message, user_prefix, settings, tmp_dir
            )
            print("Manuscript translation completed.")

            # Build the final version of the edited manuscript
            print("Building the edited manuscript...")
            merge_groups_and_save(
                args.filename,
                action,
                settings["output_dir"],
                tmp_dir,
                include_original=False,
            )
            print("Translated manuscript saved.")

        elif args.command == "build":
            settings = load_settings(require_api=False)
            action = args.language or "BUILD"
            language = args.language if not args.edited else None
            tmp_dir = workspace_for(args.filename, language)
            print(f"Building final document for {args.filename}...")
            merge_groups_and_save(
                args.filename,
                action,
                settings["output_dir"],
                tmp_dir,
                include_original=args.edited,
            )
            print(f"Final document {args.filename} built and saved.")

        else:
            parser.print_help(sys.stderr)
            sys.exit(2)
    except RateLimitError as e:
        print(f"OpenAI rate limit exceeded: {e}", file=sys.stderr)
        sys.exit(1)
    except AuthenticationError:
        print("OpenAI authentication failed. Check OPENAI_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except APIConnectionError as e:
        print(f"Could not connect to OpenAI: {e}", file=sys.stderr)
        sys.exit(1)
    except APIStatusError as e:
        print(f"OpenAI API request failed ({e.status_code}): {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
