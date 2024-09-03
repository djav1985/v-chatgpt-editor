import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .api import send_to_editor

def process_manuscript(filename, system_message, user_prefix, max_workers=10):
    """Process the manuscript by sending sections from .old files to Cohere for correction and creating .new files."""
    file = os.path.splitext(os.path.basename(filename))[0]

    try:
        # Directory where temporary files are stored
        tmp_dir = f"./tmp/{file}"

        # Check if the directory exists
        if not os.path.exists(tmp_dir):
            raise Exception("Temporary directory not found.")

        # Get a list of all .old files and sort them based on their numeric prefixes
        old_files = sorted(
            [f for f in os.listdir(tmp_dir) if f.endswith(".old")],
            key=lambda x: int(x.split("-")[0]),
        )

        # Initialize corrected sections list
        corrected_sections = []

        # Count the number of '.old' files in the './tmp' directory
        total_sections = len(old_files)

        # Function to process a single file
        def process_file(old_file):
            new_filename = os.path.join(tmp_dir, old_file.replace(".old", ".new"))

            # Process only if .new file does not exist
            if not os.path.exists(new_filename):
                with open(os.path.join(tmp_dir, old_file), "r") as section_file:
                    section_text = section_file.read()

                # Dynamically count the number of '.new' files completed
                completed_sections = len([f for f in os.listdir(tmp_dir) if f.endswith(".new")])

                # Communicate with Cohere API to get the corrected text
                corrected_text = send_to_editor(
                    section_text,
                    completed_sections,
                    total_sections,
                    system_message,
                    user_prefix,
                )

                # Write the corrected text to a new .new file
                with open(new_filename, "w") as new_section_file:
                    new_section_file.write(corrected_text)

            else:
                # If .new file already exists, read the corrected text from it
                with open(new_filename, "r") as new_section_file:
                    corrected_text = new_section_file.read()

            return corrected_text

        # Use ThreadPoolExecutor to process files concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file, old_file): old_file for old_file in old_files}
            for future in as_completed(future_to_file):
                old_file = future_to_file[future]
                try:
                    corrected_text = future.result()
                    corrected_sections.append(corrected_text)
                except Exception as e:
                    print(f"Error processing file {old_file}: {e}")

        # Return the list of all corrected sections
        return corrected_sections

    except Exception as e:
        # Raise an exception with detailed error information if any error occurs
        raise Exception(f"Error processing manuscript: {e}")
