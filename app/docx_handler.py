import os
import re
import difflib
import json
from docx.shared import Inches, Pt, RGBColor
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load the environment variables
load_dotenv()


def clean_tags(text):
    """Remove empty tags and ensure proper tag formatting."""
    # Remove tags that are empty or contain only spaces
    text = re.sub(r"<(\w+)[^>]*>\s*</\1>", "", text)

    # Ensure there are no spaces after the opening tag or before the closing tag
    text = re.sub(r">\s+", ">", text)
    text = re.sub(r"\s+<", "<", text)

    return text


def split_into_sections(filename, section_size):
    file = os.path.splitext(os.path.basename(filename))[0]
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

            # Clean the tags
            styled_text = clean_tags(styled_text)

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
            if os.path.exists(old_filename):
                print(f"File {old_filename} already exists. Skipping...")
                continue  # Skip if file already exists
            with open(old_filename, "w") as file:
                file.write("\n".join(section))

        return sections

    except Exception as e:
        raise Exception(f"Error processing document: {e}")

def split_into_chapters(filename):
    """
    Load a DOCX file, split it into chapters based on 'Heading 1',
    and create chapter#.txt files.
    """
    file = os.path.splitext(os.path.basename(filename))[0]
    tmp_dir = f"./tmp/{file}"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    try:
        edited_file = os.path.join(os.getenv("OUTPUT_DIR", "./output"), f"{os.path.basename(filename)}")
        doc = Document(edited_file)
        chapter_number = 1
        chapter_content = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip() == "":  # Skip empty paragraphs
                continue

            # Process paragraph styles and formatting
            runs = paragraph.runs
            if not runs:
                continue

            styled_text = "".join(run.text for run in runs)

            if paragraph.style.name == "Heading 1":
                chapter_filename = os.path.join(tmp_dir, f"chapter{chapter_number}.txt")
                if os.path.exists(chapter_filename):
                    print(f"File {chapter_filename} already exists. Skipping...")
                    chapter_number += 1
                    continue

                if chapter_content:  # If there is content in the current chapter, save it
                    with open(chapter_filename, "w") as chapter_file:
                        chapter_file.write("\n".join(chapter_content))
                    print(f"Created {chapter_filename}")
                    chapter_content = []  # Reset for the next chapter
                    chapter_number += 1

            # Append the styled text to the chapter content
            chapter_content.append(styled_text)

        # Save the last chapter if there is remaining content after the loop
        if chapter_content:
            chapter_filename = os.path.join(tmp_dir, f"chapter{chapter_number}.txt")
            if not os.path.exists(chapter_filename):
                with open(chapter_filename, "w") as chapter_file:
                    chapter_file.write("\n".join(chapter_content))
                print(f"Created {chapter_filename}")

    except Exception as e:
        raise Exception(f"Error processing document: {e}")


def replace_quotes_with_curly(text):
    """Replace straight quotes with curly quotes intelligently."""
    curly_quote = "“"
    in_quote = False
    new_text = ""
    for char in text:
        if char == '"':
            if not in_quote:
                new_text += "“"  # opening quote
                in_quote = True
            else:
                new_text += "”"  # closing quote
                in_quote = False
        else:
            new_text += char
    return new_text


def create_run(para, fragment, styles):
    """Create a formatted run in a paragraph, applying bold and italic styles."""
    text = replace_quotes_with_curly(fragment)
    run = para.add_run(text)
    run.bold = "b" in styles
    run.italic = "i" in styles


def process_overlapping_tags(text):
    """Process text with overlapping tags and return text fragments with style info."""
    style_flags = {"b": False, "i": False}
    fragments = []
    current_text = ""
    i = 0

    while i < len(text):
        if text.startswith("<b>", i):
            if current_text:  # Append text before the bold tag as a fragment.
                fragments.append(
                    (current_text, "".join(k for k, v in style_flags.items() if v))
                )
                current_text = ""
            style_flags["b"] = True
            i += 3  # Skip the <b> tag
        elif text.startswith("</b>", i):
            if (
                current_text
            ):  # Append text before the closing bold tag as a bold fragment.
                fragments.append(
                    (current_text, "".join(k for k, v in style_flags.items() if v))
                )
                current_text = ""
            style_flags["b"] = False
            i += 4  # Skip the </b> tag
        elif text.startswith("<i>", i):
            if current_text:
                fragments.append(
                    (current_text, "".join(k for k, v in style_flags.items() if v))
                )
                current_text = ""
            style_flags["i"] = True
            i += 3  # Skip the <i> tag
        elif text.startswith("</i>", i):
            if current_text:
                fragments.append(
                    (current_text, "".join(k for k, v in style_flags.items() if v))
                )
                current_text = ""
            style_flags["i"] = False
            i += 4  # Skip the </i> tag
        else:
            current_text += text[i]
            i += 1

    if current_text:  # Append any remaining text as a fragment.
        fragments.append(
            (current_text, "".join(k for k, v in style_flags.items() if v))
        )

    return fragments


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
                        if line.startswith("<title>") and line.endswith("</title>"):
                            line_content = line[7:-8]
                            para = doc.add_heading(line_content, level=1)
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        elif line.startswith("<h1>") and line.endswith("</h1>"):
                            doc.add_page_break()
                            para = doc.add_heading(line[4:-5], level=1)
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        elif line.startswith("<h2>") and line.endswith("</h2>"):
                            para = doc.add_heading(line[4:-5], level=2)
                        elif line.startswith("<center>") and line.endswith("</center>"):
                            line_content = line[8:-9]
                            para = doc.add_paragraph()
                            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            para.add_run(line_content)
                        elif line.startswith("<p>") and line.endswith("</p>"):
                            line_content = line[3:-4]
                            para = doc.add_paragraph()
                            para.paragraph_format.first_line_indent = Inches(0.20)
                            # Ensure to define or adjust process_overlapping_tags and create_run
                            fragments = process_overlapping_tags(line_content)
                            for fragment, styles in fragments:
                                create_run(para, fragment, styles)
                        else:
                            continue

            # Save the combined document
            combined_filename = os.path.join(
                output_dir, f"{prefix}{os.path.basename(filename)}"
            )
            doc.save(combined_filename)
            print(f"Combined DOCX {combined_filename} saved.")

    except Exception as e:
        print(f"Error in document merging and saving: {e}")
        raise


def format_section_title(title):
    """Format section titles by adding spaces between capitalized words."""
    return re.sub(r"(?<!^)(?=[A-Z])", " ", title).strip()

def json_report_to_docx(filename):
    """
    Convert a JSON report into a DOCX file and save it in the specified output directory.
    """
    # Determine the base file name and paths
    file_base = os.path.splitext(os.path.basename(filename))[0]
    tmp_dir = f"./tmp/{file_base}"
    json_report_path = os.path.join(tmp_dir, f"REPORT_{file_base}.json")

    output_dir = os.getenv("OUTPUT_DIR", "./output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_docx_filename = f"REPORT_{file_base}.docx"
    output_docx_path = os.path.join(output_dir, output_docx_filename)

    try:
        # Load JSON report data
        with open(json_report_path, "r") as json_file:
            report_data = json.load(json_file)

        # Create a new Document
        doc = Document()
        report_title = list(report_data.keys())[0]

        # Add header to every page
        section = doc.sections[0]
        header = section.header
        header_paragraph = header.paragraphs[0]
        header_run = header_paragraph.add_run(report_title)
        header_run.font.size = Pt(12)
        header_run.bold = True
        header_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add footer to every page
        footer = section.footer
        footer_paragraph = footer.paragraphs[0]
        footer_run = footer_paragraph.add_run("Eddie The Editor AI by Vontainment.com")
        footer_run.font.size = Pt(8)  # Small font size
        footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT  # Left justified

        # Add chapters with a page break before each new chapter, except the first one
        chapters = report_data[report_title]
        first_chapter = True

        for chapter_title, chapter_content in chapters.items():
            has_content = False  # Reset content flag for each chapter

            # Correctly format chapter titles (e.g., "Chapter 1")
            formatted_chapter_title = re.sub(r"chapter(\d+)", r"Chapter \1", chapter_title, flags=re.IGNORECASE)

            # Add a page break before each chapter except the first one
            if not first_chapter:
                doc.add_page_break()
            first_chapter = False  # Set first_chapter to False after the first chapter

            # Chapter title with Heading 1 style, centered
            chapter_paragraph = doc.add_paragraph(formatted_chapter_title, style='Heading 1')
            chapter_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add space after chapter title
            doc.add_paragraph("\n")

            # Add section content
            for section_title, section_content in chapter_content.items():
                if section_title == "ChapterOverview":
                    doc.add_paragraph("Chapter Overview", style='Heading 2')  # Add the Chapter Overview title
                    overview = section_content.get("Overview", "")
                    actionable_recommendations = section_content.get("ActionableRecommendations", [])
                    if overview:
                        # Add the overview
                        overview_paragraph = doc.add_paragraph(overview)
                        overview_paragraph.style = doc.styles['Normal']
                        for run in overview_paragraph.runs:
                            run.font.size = Pt(10)
                        has_content = True

                    # Only add Actionable Recommendations if they are not empty
                    if actionable_recommendations:
                        recommendations_paragraph = doc.add_paragraph("Actionable Recommendations:", style='Heading 3')
                        recommendations_run = recommendations_paragraph.runs[0]
                        recommendations_run.bold = True
                        recommendations_run.font.size = Pt(8)  # Set font size to 8
                        recommendations_run.font.color.rgb = RGBColor(255, 0, 0)  # Red color

                        # List each recommendation as a bullet point
                        for recommendation in actionable_recommendations:
                            recommendation_paragraph = doc.add_paragraph(f"• {recommendation}", style='List Bullet')
                            recommendation_run = recommendation_paragraph.runs[0]
                            recommendation_run.font.size = Pt(8)
                            recommendation_run.font.color.rgb = RGBColor(255, 109, 0)  # Orange color
                            has_content = True

                # Check if the section is either ConsistencyInNarrativeElements or DetailConsistencyCheck
                elif section_title in ["ConsistencyInNarrativeElements", "DetailConsistencyCheck"]:
                    # Include the section only if it's not None
                    if section_content is not None:
                        overview = section_content.get("Overview", "")
                        actionable_recommendations = section_content.get("ActionableRecommendations", [])
                        if overview:
                            section_paragraph = doc.add_paragraph(format_section_title(section_title), style='Heading 2')
                            section_paragraph.paragraph_format.space_before = Pt(24)

                            overview_paragraph = doc.add_paragraph(overview)
                            overview_paragraph.style = doc.styles['Normal']
                            for run in overview_paragraph.runs:
                                run.font.size = Pt(10)
                            has_content = True

                        if actionable_recommendations:
                            recommendations_paragraph = doc.add_paragraph("Actionable Recommendations:", style='Heading 3')
                            recommendations_run = recommendations_paragraph.runs[0]
                            recommendations_run.bold = True
                            recommendations_run.font.size = Pt(8)
                            recommendations_run.font.color.rgb = RGBColor(255, 0, 0)  # Red color

                            for recommendation in actionable_recommendations:
                                recommendation_paragraph = doc.add_paragraph(f"• {recommendation}", style='List Bullet')
                                recommendation_run = recommendation_paragraph.runs[0]
                                recommendation_run.font.size = Pt(8)
                                recommendation_run.font.color.rgb = RGBColor(255, 109, 0)  # Orange color
                                has_content = True

            # Ensure chapters with no actual content do not add blank pages
            if not has_content:
                # Remove the last added paragraph if it was added with no content
                last_paragraph = doc.paragraphs[-1]
                if not last_paragraph.text.strip():  # Remove if the last paragraph is empty
                    doc._element.remove(last_paragraph._element)

        # Save the document if it contains any content
        if len(doc.paragraphs) > 0:
            doc.save(output_docx_path)
            print(f"Report saved to {output_docx_path}")
        else:
            print("No content to save, document is empty.")

    except Exception as e:
        print(f"Error generating DOCX report: {e}")
