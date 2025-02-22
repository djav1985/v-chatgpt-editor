import os
import re
from pathlib import Path
from docx.shared import Inches, Pt
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from dotenv import load_dotenv
from api import communicate_with_openai

# Load the environment variables
load_dotenv()


def split_into_sections(filename: str, section_size: int) -> list:
    """
    Splits a DOCX document into sections based on a specified token size.
    Args:
        filename (str): The path to the DOCX file to be split.
        section_size (int): The maximum number of tokens per section.
    Returns:
        list: A list of sections, where each section is a list of styled text paragraphs.
    Raises:
        Exception: If there is an error processing the document.
    The function performs the following steps:
    1. Extracts the base name of the file and creates a temporary directory.
    2. Opens the DOCX document and initializes variables for sections and tokens.
    3. Iterates through each paragraph in the document, applying styles (bold, italic, title, headings, and alignment).
    4. Splits the document into sections based on the specified token size.
    5. Writes each section to a temporary file.
    6. Returns the list of sections.
    """
    file: str = os.path.splitext(os.path.basename(filename))[0]
    tmp_dir: str = f"./tmp/{file}"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    try:
        doc: Document = Document(filename)
        sections: list = []
        current_section: list = []
        current_tokens: int = 0

        for paragraph in doc.paragraphs:
            runs = paragraph.runs
            if not runs:
                continue

            styled_text: str = ""
            open_tags = []

            def close_tags():
                nonlocal styled_text
                while open_tags:
                    styled_text += f"</{open_tags.pop()}>"

            for run in runs:
                run_text: str = run.text
                if run.bold and "b" not in open_tags:
                    styled_text += "<b>"
                    open_tags.append("b")
                elif not run.bold and "b" in open_tags:
                    styled_text += "</b>"
                    open_tags.remove("b")
                if run.italic and "i" not in open_tags:
                    styled_text += "<i>"
                    open_tags.append("i")
                elif not run.italic and "i" in open_tags:
                    styled_text += "</i>"
                    open_tags.remove("i")

                styled_text += run_text

            close_tags()

            if paragraph.style.name == "Title":
                styled_text = f"<title>{styled_text}</title>"
            elif paragraph.style.name.startswith("Heading"):
                header_level: str = re.findall(r"\d+", paragraph.style.name)[0]
                styled_text = f"<h{header_level}>{styled_text}</h{header_level}>"
            else:
                try:
                    if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                        styled_text = f"<center>{styled_text}</center>"
                    else:
                        styled_text = f"<p>{styled_text}</p>"
                except:
                    styled_text = f"<p>{styled_text}</p>"

            if styled_text == "<p></p>" or styled_text == "<center></center>":
                continue  # Discard empty tags

            new_tokens: int = len(styled_text.split())
            if current_tokens + new_tokens > section_size:
                sections.append(current_section)
                current_section = []
                current_tokens = 0

            current_section.append(styled_text)
            current_tokens += new_tokens

        if current_section:
            sections.append(current_section)

        for i, section in enumerate(sections, start=1):
            old_filename: str = os.path.join(tmp_dir, f"{i}-section.old")
            with open(old_filename, "w") as file:
                file.write("\n".join(section))

        return sections

    except Exception as e:
        raise Exception(f"Error processing document: {e}")


def merge_groups_and_save(filename: str, action: str) -> None:
    """
    Merges text sections from temporary files into a single DOCX document and saves it.

    Args:
        filename (str): The name of the input file to process.
        action (str): Action to determine the prefix for the output file.

    Raises:
        Exception: If an error occurs during document merging and saving.
    """
    file_base: str = os.path.splitext(os.path.basename(filename))[0]
    try:
        tmp_dir: Path = Path(f"./tmp/{file_base}")
        output_dir: Path = Path(f"./output/{file_base}")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created output directory: {output_dir}")

        for file_type in [".new", ".old"]:
            prefix: str = f"{action.upper()}_" if file_type == ".new" else "ORIGINAL_"
            doc: Document = Document()

            files = sorted(
                [p for p in tmp_dir.iterdir() if p.suffix == file_type],
                key=lambda p: int(p.stem.split("-")[0]),
            )

            for file_path in files:
                print(f"Processing {file_path.name}...")
                with file_path.open("r") as section_file:
                    text_content: list = section_file.read().splitlines()

                para = None
                for line in text_content:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("<title>") and line.endswith("</title>"):
                        para = doc.add_heading(line[7:-8], level=1)
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        para.paragraph_format.space_after = Pt(14)
                    elif line.startswith("<h1>") and line.endswith("</h1>"):
                        doc.add_page_break()
                        para = doc.add_heading(line[4:-5], level=1)
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        para.paragraph_format.space_after = Pt(14)
                    elif line.startswith("<h2>") and line.endswith("</h2>"):
                        para = doc.add_heading(line[4:-5], level=2)
                        para.paragraph_format.space_after = Pt(12)
                    elif (
                        line.startswith("<center>") and line.endswith("</center>")
                    ) or (line.startswith("<p>") and line.endswith("</p>")):
                        tag_length: int = 8 if line.startswith("<center>") else 3
                        tag_end_length: int = 9 if line.startswith("<center>") else 4
                        line_content: str = line[tag_length:-tag_end_length]
                        para = doc.add_paragraph()
                        para.alignment = (
                            WD_ALIGN_PARAGRAPH.CENTER if tag_length == 8 else None
                        )
                        para.paragraph_format.first_line_indent = (
                            Inches(0.20) if tag_length == 3 else None
                        )

                        fragments: list = []
                        current_text: str = ""
                        styles: list = []
                        i: int = 0
                        while i < len(line_content):
                            if line_content.startswith("<b>", i):
                                if current_text:
                                    fragments.append((current_text, styles.copy()))
                                    current_text = ""
                                styles.append("b")
                                i += 3
                            elif line_content.startswith("</b>", i):
                                if current_text:
                                    fragments.append((current_text, styles.copy()))
                                    current_text = ""
                                if "b" in styles:
                                    styles.remove("b")
                                i += 4
                            elif line_content.startswith("<i>", i):
                                if current_text:
                                    fragments.append((current_text, styles.copy()))
                                    current_text = ""
                                styles.append("i")
                                i += 3
                            elif line_content.startswith("</i>", i):
                                if current_text:
                                    fragments.append((current_text, styles.copy()))
                                    current_text = ""
                                if "i" in styles:
                                    styles.remove("i")
                                i += 4
                            else:
                                current_text += line_content[i]
                                i += 1

                        if current_text:
                            fragments.append((current_text, styles.copy()))

                        for fragment, styles in fragments:
                            run = para.add_run(fragment)
                            run.bold = "b" in styles
                            run.italic = "i" in styles

            combined_filename: Path = (
                output_dir / f"{prefix}{os.path.basename(filename)}"
            )
            doc.save(str(combined_filename))
            print(f"Combined DOCX {combined_filename} saved.")
    except Exception as e:
        print(f"Error in document merging and saving: {e}")


def process_manuscript(filename: str, system_message: str, user_prefix: str) -> list:
    """
    Process the manuscript by sending sections from .old files to OpenAI for correction and creating .new files.

    Args:
        filename (str): The name of the manuscript file.
        system_message (str): The system message to be sent to OpenAI.
        user_prefix (str): The user prefix for communicating with OpenAI.

    Returns:
        list: A list of corrected sections.

    Raises:
        Exception: If the temporary directory is not found or any other error occurs.
    """
    file_base: str = os.path.splitext(os.path.basename(filename))[0]
    try:
        tmp_dir: Path = Path(f"./tmp/{file_base}")
        if not tmp_dir.exists():
            raise Exception("Temporary directory not found.")

        # Perform a single scan of the tmp directory.
        all_files = list(tmp_dir.iterdir())
        old_files = sorted(
            [p for p in all_files if p.suffix == ".old"],
            key=lambda p: int(p.stem.split("-")[0]),
        )
        # Cache .new file names to avoid rescanning each time.
        new_files = {p.name for p in all_files if p.suffix == ".new"}

        corrected_sections: list = []
        total_sections: int = len(old_files)

        for old_file in old_files:
            new_file: Path = old_file.with_suffix(".new")
            # Count completed sections from cached new_files.
            completed_sections: int = sum(
                1 for name in new_files if name.endswith(".new")
            )

            if not new_file.exists():
                with old_file.open("r") as section_file:
                    section_text: str = section_file.read()

                corrected_text: str = communicate_with_openai(
                    section_text,
                    completed_sections,
                    total_sections,
                    system_message,
                    user_prefix,
                )

                print(f"Response From API:\n{corrected_text}")
                with new_file.open("w") as new_section_file:
                    new_section_file.write(corrected_text)
                # Update cache for completed sections.
                new_files.add(new_file.name)
            else:
                with new_file.open("r") as new_section_file:
                    corrected_text = new_section_file.read()

            corrected_sections.append(corrected_text)

        return corrected_sections

    except Exception as e:
        raise Exception(f"Error processing manuscript: {e}")
