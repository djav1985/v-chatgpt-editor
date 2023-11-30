# docx_handler.py
import os
from dotenv import load_dotenv  # Load environment variables
from docx import Document  # To process docx files

from api import communicate_with_openai
import re

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
            # Process paragraph text and wrap in HTML tags
            text = paragraph.text
            if paragraph.style.name == 'Title':
                text = f"<title>{text}</title>"
            elif paragraph.style.name.startswith('Heading'):
                header_level = paragraph.style.name[-1]
                text = f"<h{header_level}>{text}</h{header_level}>"
            else:
                text = f"<p>{text}</p>"
                # Check if the paragraph is centered and add <centered> tags
                if paragraph.alignment == 1:  # 1 represents centered alignment
                    text = f"<centered>{text}</centered>"

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
    """Merge the corrected texts from .new files and preserve formatting, headers, paragraphs, and more, save to a new DOCX file."""
    try:
        tmp_dir = './tmp'
        edited_filename = f"EDITED_{filename}"
        edited_doc = Document()

        # Get a list of all .new files and sort them based on their numeric prefixes
        new_files = sorted([f for f in os.listdir(tmp_dir) if f.endswith('.new')], key=lambda x: int(x.split('-')[0]))

        for new_file in new_files:
            with open(os.path.join(tmp_dir, new_file), 'r') as section_file:
                corrected_text = section_file.read()

            # Process the corrected text and apply corresponding style
            paragraphs = re.split(r'</?centered>', corrected_text)
            for i, para_text in enumerate(paragraphs):
                if i % 2 == 1:  # Check if it's enclosed in <centered> </centered> tags
                    para = edited_doc.add_paragraph(para_text)
                    para.alignment = 1  # Set alignment to centered
                else:
                    # Remove HTML tags and extract content
                    para_text_without_tags = re.sub(r'<.*?>', '', para_text)
                    para = edited_doc.add_paragraph(para_text_without_tags)

                    # Apply corresponding style based on the presence of headers
                    if para_text.startswith('<title>'):
                        para.style = 'Title'
                    elif para_text.startswith('<h'):
                        header_level = int(para_text[3])  # Extract header level from "<hX>"
                        para.style = f'Heading {header_level}'
                        # Add a page break before Header 1 (h1)
                        if header_level == 1:
                            edited_doc.add_page_break()
                    else:
                        para.style = 'Normal'

        edited_doc.save(edited_filename)
        print(f"DOCX {edited_filename} saved.")

    except Exception as e:
        raise Exception(f"Error merging and saving document: {e}")
