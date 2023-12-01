# docx_handler.py
import os
import re
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from dotenv import load_dotenv
from api import communicate_with_openai


# Load the environment variables
load_dotenv()

# Get the maximum tokens to be considered as a section and the path for output files as environment variables
max_tokens = int(os.getenv('SECTION_SIZE', 1024))
output_dir = os.getenv('OUTPUT_DIR', './output')

def split_into_sections(filename):
    """Load a DOCX file, split it into sections, and create .old files."""
    try:
        doc = Document(filename)
        sections = []
        current_section = []
        current_tokens = 0

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue

            if paragraph.style.name == 'Title':
                text = f"<title>{text}</title>"
            elif paragraph.style.name.startswith('Heading'):
                header_level = re.findall(r'\d+', paragraph.style.name)[0]
                text = f"<h{header_level}>{text}</h{header_level}>"
            else:
                try:
                    # Attempt to check alignment
                    if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                        text = f"<center>{text}</center>"
                    else:
                        text = f"<p>{text}</p>"
                except:
                    # Fallback to default if there's an error
                    text = f"<p>{text}</p>"

            new_tokens = len(text.split())
            if current_tokens + new_tokens > max_tokens:
                sections.append(current_section)
                current_section = []
                current_tokens = 0

            current_section.append(text)
            current_tokens += new_tokens

        if current_section:
            sections.append(current_section)

        # Create .old files for each section
        for i, section in enumerate(sections, start=1):
            old_filename = f"./tmp/{i}-section.old"
            with open(old_filename, 'w') as file:
                file.write('\n'.join(section))

        return sections

    except Exception as e:
        raise Exception(f"Error processing document: {e}")

def process_manuscript():
    """Process the manuscript by sending sections from .old files to OpenAI for correction and creating .new files."""
    try:
        # Directory where temporary files are stored
        tmp_dir = './tmp'

        # Check if the directory exists
        if not os.path.exists(tmp_dir):
            raise Exception("Temporary directory not found.")

        # Get a list of all .old files and sort them based on their numeric prefixes
        old_files = sorted([f for f in os.listdir(tmp_dir) if f.endswith('.old')], key=lambda x: int(x.split('-')[0]))

        # Initialize corrected sections list
        corrected_sections = []

        # Count the number of '.old' files in the './tmp' directory
        total_sections = len(old_files)

        # Process each .old file
        for old_file in old_files:
            new_filename = os.path.join(tmp_dir, old_file.replace('.old', '.new'))

            # Count the number of '.new' files inside the loop
            completed_sections = len([f for f in os.listdir(tmp_dir) if f.endswith('.new')])

            # Process only if .new file does not exist
            if not os.path.exists(new_filename):
                with open(os.path.join(tmp_dir, old_file), 'r') as section_file:
                    section_text = section_file.read()

                corrected_text = communicate_with_openai(section_text, completed_sections, total_sections)

                # Print the corrected text before writing to file
                print(f"Response From API:\n{corrected_text}")

                with open(new_filename, 'w') as new_section_file:
                    new_section_file.write(corrected_text)

            else:
                with open(new_filename, 'r') as new_section_file:
                    corrected_text = new_section_file.read()

            corrected_sections.append(corrected_text)

        return corrected_sections

    except Exception as e:
        raise Exception(f"Error processing manuscript: {e}")

def merge_groups_and_save(filename):
    """Merge and format texts from .new files into a DOCX file."""
    try:
        input_dir = './tmp'
        output_dir = './output'
        edited_filename = os.path.join(output_dir, f"EDITED_{os.path.basename(filename)}")
        edited_doc = Document()

        new_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.new')],
                           key=lambda x: int(x.split('-')[0]))

        for new_file in new_files:
            with open(os.path.join(input_dir, new_file), 'r') as section_file:
                corrected_text = section_file.read().splitlines()

            for line in corrected_text:
                line = line.strip()
                para = None  # Initialize para variable

                if line.startswith('<title>') and line.endswith('</title>'):
                    edited_doc.add_heading(line.replace('<title>', '').replace('</title>', ''), level=1)
                    para = edited_doc.paragraphs[-1]  # Get the last paragraph
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('<h1>') and line.endswith('</h1>'):
                    edited_doc.add_page_break()
                    edited_doc.add_heading(line.replace('<h1>', '').replace('</h1>', ''), level=1)
                    para = edited_doc.paragraphs[-1]  # Get the last paragraph
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('<h2>') and line.endswith('</h2>'):
                    edited_doc.add_heading(line.replace('<h2>', '').replace('</h2>', ''), level=2)
                    para = edited_doc.paragraphs[-1]  # Get the last paragraph
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('<center>') and line.endswith('</center>'):
                    para = edited_doc.add_paragraph(line.replace('<center>', '').replace('</center>', ''))
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif line.startswith('<p>') and line.endswith('</p>'):
                    para = edited_doc.add_paragraph(line.replace('<p>', '').replace('</p>', ''))
                    para.paragraph_format.first_line_indent = Inches(0.20)

        edited_doc.save(edited_filename)
        print(f"DOCX {edited_filename} saved.")

    except Exception as e:
        raise Exception(f"Error in document merging and saving: {e}")