# main.py
import argparse
import os
from docx_handler import process_manuscript, merge_groups_and_save, split_into_sections

if __name__ == "__main__":
    print("Initializing manuscript editor.")

    parser = argparse.ArgumentParser(description="Process a manuscript file in DOCX format.")
    parser.add_argument('--filename', type=str, help='Provide the path to your DOCX file.')
    parser.add_argument('--build', action='store_true', help='Flag to trigger building the edited manuscript.')
    args = parser.parse_args()

    if not args.filename:
        print("Error: You must provide a --filename.")
    elif not os.path.exists(args.filename):
        print(f"Error: The file {args.filename} does not exist.")
    else:
        try:
            # Load and split the manuscript into sections, creating .old files
            sections = split_into_sections(args.filename)
            print("Manuscript loaded and split into sections...")

            # Process the manuscript sections and create .new files
            corrected_manuscript = process_manuscript()
            print("Processing manuscript completed...")

            if args.build:
                # Merge corrections and save the edited manuscript
                merge_groups_and_save()
                print("Edited manuscript saved.")

        except Exception as e:
            print(f"An error occurred: {e}")
