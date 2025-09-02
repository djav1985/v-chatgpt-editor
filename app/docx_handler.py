import os
import re
import difflib
from docx.shared import Inches
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from api import communicate_with_openai

# Load the environment variables
load_dotenv()

def split_into_sections(filename, section_size):
    file = os.path.splitext(os.path.basename(filename))[0]
    # Create a directory with the name './tmp/{file}'
    tmp_dir = f"./tmp/{file}"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    """Load a DOCX file, split it into sections, and create .old files."""
    try:
        doc = Document(filename)
        sections = []
        current_section = []
        current_tokens = 0

        for paragraph in doc.paragraphs:
            runs = paragraph.runs
            if not runs:  # Check if paragraph is empty
                continue

            styled_text = ""
            for run in runs:
                run_text = run.text
                if run.bold and run.italic:
                    run_text = f"<b><i>{run_text}</i></b>"
                elif run.bold:
                    run_text = f"<b>{run_text}</b>"
                elif run.italic:
                    run_text = f"<i>{run_text}</i>"
                styled_text += run_text

            if paragraph.style.name == "Title":
                styled_text = f"<title>{styled_text}</title>"
            elif paragraph.style.name.startswith("Heading"):
                header_level = re.findall(r"\d+", paragraph.style.name)[0]
                styled_text = f"<h{header_level}>{styled_text}</h{header_level}>"
            else:
                try:
                    if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                        styled_text = f"<center>{styled_text}</center>"
                    else:
                        styled_text = f"<p>{styled_text}</p>"
                except:
                    styled_text = f"<p>{styled_text}</p>"

            new_tokens = len(styled_text.split())
            if current_tokens + new_tokens > section_size:
                sections.append(current_section)
                current_section = []
                current_tokens = 0

            current_section.append(styled_text)
            current_tokens += new_tokens

        if current_section:
            sections.append(current_section)

        # Create .old files for each section
        for i, section in enumerate(sections, start=1):
            old_filename = os.path.join(tmp_dir, f"{i}-section.old")
            with open(old_filename, "w") as file:
                file.write("\n".join(section))

        return sections

    except Exception as e:
        raise Exception(f"Error processing document: {e}")

def process_manuscript(filename, system_message, user_prefix):
    file = os.path.splitext(os.path.basename(filename))[0]
    print(f"[process_manuscript] Starting processing for: {filename}")
    try:
        # Directory where temporary files are stored
        tmp_dir = f"./tmp/{file}"

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
        corrected_sections = []

        # Count the number of '.old' files in the './tmp' directory
        total_sections = len(old_files)

        # Process each .old file
        for old_file in old_files:
            print(f"[process_manuscript] Processing section file: {old_file}")
            new_filename = os.path.join(tmp_dir, old_file.replace(".old", ".new"))

            # Count the number of '.new' files inside the loop
            completed_sections = len(
                [f for f in os.listdir(tmp_dir) if f.endswith(".new")]
            )

            # Process only if .new file does not exist
            if not os.path.exists(new_filename):
                with open(os.path.join(tmp_dir, old_file), "r") as section_file:
                    section_text = section_file.read()
                print(f"[process_manuscript] Section text length: {len(section_text)}")

                corrected_text = communicate_with_openai(
                    section_text,
                    completed_sections,
                    total_sections,
                    system_message,
                    user_prefix,
                )

                # Print the corrected text before writing to file
                print(f"[process_manuscript] Response From API:\n{corrected_text}")

                with open(new_filename, "w") as new_section_file:
                    new_section_file.write(corrected_text)

            else:
                print(f"[process_manuscript] .new file already exists for section: {old_file}")
                with open(new_filename, "r") as new_section_file:
                    corrected_text = new_section_file.read()

            corrected_sections.append(corrected_text)

        print(f"[process_manuscript] Finished processing all sections.")
        return corrected_sections

    except Exception as e:
        print(f"[process_manuscript] Exception: {e}")
        raise Exception(f"Error processing manuscript: {e}")

def merge_groups_and_save(filename, action):
    file = os.path.splitext(os.path.basename(filename))[0]
    try:
        tmp_dir = f"./tmp/{file}"
        output_dir = os.getenv("OUTPUT_DIR", "./output")

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        # Process both .new and .old files
        for file_type in [".new", ".old"]:
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
                with open(os.path.join(tmp_dir, file), "r") as section_file:
                    text_content = section_file.read().splitlines()

                para = None
                for line in text_content:
                    line = line.strip()
                    if line:
                        # Process <title> tags
                        if line.startswith("<title>") and line.endswith("</title>"):
                            line_content = line[7:-8]
                            para = doc.add_heading(line_content, level=1)
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER

                        # Process <h1> and <h2> tags
                        elif line.startswith("<h1>") and line.endswith("</h1>"):
                            doc.add_page_break()
                            para = doc.add_heading(line[4:-5], level=1)
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        elif line.startswith("<h2>") and line.endswith("</h2>"):
                            para = doc.add_heading(line[4:-5], level=2)

                        # Process <center> tags
                        elif line.startswith("<center>") and line.endswith("</center>"):
                            line_content = line[8:-9]  # Remove <center> and </center>
                            para = doc.add_paragraph()
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            # Process the content inside <center> tags for bold and italic
                            fragments = []
                            current_text = ""
                            styles = ""
                            i = 0
                            while i < len(line_content):
                                if line_content.startswith("<b>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = "b"  # Mark bold style
                                    i += 3  # Skip <b> tag
                                elif line_content.startswith("</b>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = ""  # Reset styles after closing </b> tag
                                    i += 4  # Skip </b> tag
                                elif line_content.startswith("<i>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = "i"  # Mark italic style
                                    i += 3  # Skip <i> tag
                                elif line_content.startswith("</i>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = ""  # Reset styles after closing </i> tag
                                    i += 4  # Skip </i> tag
                                else:
                                    current_text += line_content[i]  # Collect non-tag content
                                    i += 1
                            if current_text:
                                fragments.append((current_text, styles))

                            # Apply styles
                            for fragment, styles in fragments:
                                # Replace straight quotes with curly quotes
                                text = ""
                                curly_quote = "“"
                                in_quote = False
                                for char in fragment:
                                    if char == '"':
                                        if not in_quote:
                                            text += "“"  # opening quote
                                            in_quote = True
                                        else:
                                            text += "”"  # closing quote
                                            in_quote = False
                                    else:
                                        text += char

                                # Create a run with the formatted text
                                run = para.add_run(text)
                                if 'b' in styles:
                                    run.bold = True
                                if 'i' in styles:
                                    run.italic = True

                        # Process <p> tags
                        elif line.startswith("<p>") and line.endswith("</p>"):
                            line_content = line[3:-4]  # Remove <p> and </p>
                            para = doc.add_paragraph()
                            para.paragraph_format.first_line_indent = Inches(0.20)
                            # Process the content inside <p> tags for bold and italic
                            fragments = []
                            current_text = ""
                            styles = ""
                            i = 0
                            while i < len(line_content):
                                if line_content.startswith("<b>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = "b"  # Mark bold style
                                    i += 3  # Skip <b> tag
                                elif line_content.startswith("</b>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = ""  # Reset styles after closing </b> tag
                                    i += 4  # Skip </b> tag
                                elif line_content.startswith("<i>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = "i"  # Mark italic style
                                    i += 3  # Skip <i> tag
                                elif line_content.startswith("</i>", i):
                                    if current_text:
                                        fragments.append((current_text, styles))
                                        current_text = ""
                                    styles = ""  # Reset styles after closing </i> tag
                                    i += 4  # Skip </i> tag
                                else:
                                    current_text += line_content[i]  # Collect non-tag content
                                    i += 1
                            if current_text:
                                fragments.append((current_text, styles))

                            # Apply styles
                            for fragment, styles in fragments:
                                # Replace straight quotes with curly quotes
                                text = ""
                                curly_quote = "“"
                                in_quote = False
                                for char in fragment:
                                    if char == '"':
                                        if not in_quote:
                                            text += "“"  # opening quote
                                            in_quote = True
                                        else:
                                            text += "”"  # closing quote
                                            in_quote = False
                                    else:
                                        text += char

                                # Create a run with the formatted text
                                run = para.add_run(text)
                                if 'b' in styles:
                                    run.bold = True
                                if 'i' in styles:
                                    run.italic = True

            # Save the combined document
            combined_filename = os.path.join(
                output_dir, f"{prefix}{os.path.basename(filename)}"
            )
            doc.save(combined_filename)
            print(f"Combined DOCX {combined_filename} saved.")

    except Exception as e:
        print(f"Error in document merging and saving: {e}")
