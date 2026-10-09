import hashlib
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from docx import Document

from api import communicate_with_openai, get_client
from docx_markup import add_markup_line, serialize_paragraph
from token_count import count_model_tokens


def split_into_sections(
    filename: str,
    max_tokens: int,
    cache_key: str = "",
    model_name: str = "gpt-5-mini",
    tmp_dir: str | None = None,
) -> list[list[str]]:
    """Split a DOCX into paragraph-preserving sections under a token budget."""
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("The maximum token budget must be a positive integer.")

    file = os.path.splitext(os.path.basename(filename))[0]
    tmp_dir = tmp_dir or f"./tmp/{file}"
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        doc = Document(filename)
        sections: list[list[str]] = []
        current_section: list[str] = []

        for paragraph_number, paragraph in enumerate(doc.paragraphs, start=1):
            styled_text = serialize_paragraph(paragraph, tmp_dir)
            if styled_text is None:  # Empty paragraph
                continue

            paragraph_tokens = count_model_tokens(styled_text, model_name)
            if paragraph_tokens > max_tokens:
                warnings.warn(
                    f"Paragraph {paragraph_number} contains {paragraph_tokens} "
                    f"tokens, exceeding the {max_tokens}-token section budget; "
                    "keeping it intact.",
                    UserWarning,
                )

            if current_section:
                candidate_section = "\n".join([*current_section, styled_text])
                if count_model_tokens(candidate_section, model_name) > max_tokens:
                    sections.append(current_section)
                    current_section = []

            current_section.append(styled_text)

        if current_section:
            sections.append(current_section)

        source_hash = hashlib.sha256()
        with open(filename, "rb") as source_file:
            for block in iter(lambda: source_file.read(1024 * 1024), b""):
                source_hash.update(block)
        run_identity = "\0".join(
            [
                source_hash.hexdigest(),
                str(max_tokens),
                model_name,
                cache_key,
            ]
        )
        run_signature = hashlib.sha256(run_identity.encode("utf-8")).hexdigest()
        signature_path = os.path.join(tmp_dir, ".run-signature")
        try:
            with open(signature_path, encoding="utf-8") as signature_file:
                previous_signature = signature_file.read()
        except FileNotFoundError:
            previous_signature = None

        if previous_signature != run_signature:
            for artifact in os.listdir(tmp_dir):
                if artifact.endswith((".old", ".new")):
                    os.remove(os.path.join(tmp_dir, artifact))

        with open(signature_path, "w", encoding="utf-8") as signature_file:
            signature_file.write(run_signature)

        # Create .old files for each section.
        for i, section in enumerate(sections, start=1):
            old_filename = os.path.join(tmp_dir, f"{i}-section.old")
            with open(old_filename, "w", encoding="utf-8") as old_section_file:
                old_section_file.write("\n".join(section))

        return sections

    except Exception as e:
        raise Exception(f"Error processing document: {e}")


def _process_section(
    tmp_dir: str,
    old_file: str,
    system_message: str,
    user_prefix: str,
    settings: dict[str, Any],
) -> None:
    with open(os.path.join(tmp_dir, old_file), "r", encoding="utf-8") as section_file:
        section_text = section_file.read()
    print(
        f"[process_manuscript] Processing section file: {old_file} | "
        f"Text length: {len(section_text)}"
    )

    corrected_text = communicate_with_openai(
        section_text,
        system_message,
        user_prefix,
        settings,
    )

    new_filename = os.path.join(tmp_dir, old_file.replace(".old", ".new"))
    with open(new_filename, "w", encoding="utf-8") as new_section_file:
        new_section_file.write(corrected_text)


def process_manuscript(
    filename: str,
    system_message: str,
    user_prefix: str,
    settings: dict[str, Any],
    tmp_dir: str | None = None,
) -> list[str]:
    file = os.path.splitext(os.path.basename(filename))[0]
    print(f"[process_manuscript] Starting processing for: {filename}")
    try:
        # Directory where temporary files are stored
        tmp_dir = tmp_dir or f"./tmp/{file}"

        # Check if the directory exists
        if not os.path.exists(tmp_dir):
            print(f"[process_manuscript] Temporary directory not found: {tmp_dir}")
            raise Exception("Temporary directory not found.")

        # Get a list of all .old files and sort them based on their numeric prefixes
        old_files = sorted(
            [f for f in os.listdir(tmp_dir) if f.endswith(".old")],
            key=lambda x: int(x.split("-")[0]),
        )
        print(f"[process_manuscript] Found {len(old_files)} .old files in {tmp_dir}")

        # Initialize corrected sections list
        corrected_sections: list[str] = []

        # Count the number of '.old' files in the './tmp' directory
        total_sections = len(old_files)

        def new_path(old_file: str) -> str:
            return os.path.join(tmp_dir, old_file.replace(".old", ".new"))

        # Sections that already have a .new file are resumed, not re-sent
        pending = [f for f in old_files if not os.path.exists(new_path(f))]
        print(
            f"[process_manuscript] {total_sections - len(pending)} sections already "
            f"done, {len(pending)} to send"
        )

        if pending:
            get_client(settings)
            max_concurrent = settings["max_concurrent_sections"]
            print(f"[process_manuscript] Sending up to {max_concurrent} at a time")
            completed_sections = total_sections - len(pending)
            with ThreadPoolExecutor(max_workers=max_concurrent) as pool:
                futures = [
                    pool.submit(
                        _process_section,
                        tmp_dir,
                        old_file,
                        system_message,
                        user_prefix,
                        settings,
                    )
                    for old_file in pending
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed_sections += 1
                        print(
                            "[process_manuscript] Completed/Total Sections: "
                            f"{completed_sections}/{total_sections}"
                        )
                    except Exception:
                        # Unstarted sections are dropped; in-flight ones finish
                        for other in futures:
                            other.cancel()
                        raise

        for old_file in old_files:
            with open(new_path(old_file), "r", encoding="utf-8") as new_file:
                corrected_sections.append(new_file.read())

        print("[process_manuscript] Finished processing all sections.")
        return corrected_sections

    except Exception as e:
        print(f"[process_manuscript] Exception: {e}")
        raise


def merge_groups_and_save(
    filename: str,
    action: str,
    output_dir: str,
    tmp_dir: str | None = None,
    include_original: bool = True,
) -> None:
    file = os.path.splitext(os.path.basename(filename))[0]
    try:
        tmp_dir = tmp_dir or f"./tmp/{file}"
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        file_types = [".new", ".old"] if include_original else [".new"]
        for file_type in file_types:
            prefix = f"{action.upper()}_" if file_type == ".new" else "ORIGINAL_"
            doc = Document()  # Initialize the Document outside the files loop

            # Sort files by their numeric order
            files = sorted(
                [f for f in os.listdir(tmp_dir) if f.endswith(file_type)],
                key=lambda x: int(x.split("-")[0]),
            )

            # Process files
            for file in files:
                print(f"Processing {file}...")
                with open(
                    os.path.join(tmp_dir, file), "r", encoding="utf-8"
                ) as section_file:
                    text_content = section_file.read().splitlines()

                for line in text_content:
                    line = line.strip()
                    if line:
                        if not add_markup_line(doc, line, tmp_dir):
                            raise ValueError(
                                f"Unrecognized markup in {file}: {line!r}"
                            )

            # Save the combined document
            combined_filename = os.path.join(
                output_dir, f"{prefix}{os.path.basename(filename)}"
            )
            doc.save(combined_filename)
            print(f"Combined DOCX {combined_filename} saved.")

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Error in document merging and saving: {e}") from e
