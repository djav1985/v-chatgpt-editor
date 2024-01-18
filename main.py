import os
import argparse
from docx_handler import process_manuscript, merge_groups_and_save, split_into_sections

def main():
    print("Initializing manuscript editor.")

    parser = argparse.ArgumentParser(description="Process a manuscript file in DOCX format.")
    parser.add_argument('--filename', type=str, help='Provide the path to your DOCX file.')
    parser.add_argument('--edit', action='store_true', help='Flag to trigger editing the manuscript.')
    parser.add_argument('--translate', type=str, help='Language to translate the manuscript into.')
    parser.add_argument('--build', action='store_true', help='Flag to trigger building the edited manuscript.')
    parser.add_argument('--split', type=str, choices=['translate', 'edit'], help='Split files in input directory.')
    args = parser.parse_args()

    if args.split:
        input_dir = './input'
        section_size = int("1024") if args.split == 'translate' else "256"

        for filename in os.listdir(input_dir):
            if filename.endswith('.docx'):
                file_path = os.path.join(input_dir, filename)
                sections = split_into_sections(file_path, section_size)
                print(f"{filename}: {len(sections)} sections created.")
    else:
        if args.filename:
            if not os.path.exists(args.filename):
                print(f"Error: The file {args.filename} does not exist.")
                exit(1)

        if args.edit or args.translate:
            if args.edit:
                user_prefix = f"1. Review the text for spelling (correct UK to US english), grammar, and punctuation errors. 2. Ensure correct usage and consistency with verb tense, contractions, compound words, and hyphenated words. 3. Only correct dialog/inner monologs for punctuation and spelling. 4. Ensure you do not change the style or meaning of the text. 5. Under no circumstance should you add or change adjectives except to correct the spelling. 6. Please keep newlines and HTML intact, as well as apply italic to internal monolog text with <i> </i> and mark sentences with structure errors as needing revision with <*> </*>. 7. Then output the corrected text with no comments before or after:"
                system_message  = f"You are a renowned contemporary romance book editor. You review Review the text for spelling (correct UK to US english), grammar, and punctuation errors. Ensure correct usage and consistency with verb tense, contractions, compound words, and hyphenated words. Only correct dialog/inner monologs for punctuation and spelling. Ensure you do not change the style or meaning of the text. Under no circumstance should you add or change adjectives except to correct the spelling. Please keep newlines and HTML intact, as well as apply italic to internal monolog text with <i> </i> and mark sentences with structure errors as needing revision with <*> </*>. Then output the corrected text with no comments before or after."
                max_tokens = int("2048")
                section_size = int("256")
            elif args.translate:
                user_prefix = f"1. Translate the text from English to {args.translate} with a focus on distinct cultural nuances, structural and syntactical variations, grammatical norms, idiomatic expressions, and cultural contexts of each language. 2. Maintain the original HTML structure. 3. Do not add comments surrounding the translation. 4. Ensure the translation reflects the spirit and context of the original text, beyond a literal word-for-word approach so the translation feels more natural:"
                system_message  = f"You are an expert in literary translation. Rather than adhering to a literal, word-for-word translation, deeply consider the distinct cultural nuances, structural and syntactical variations, grammatical norms, idiomatic expressions, and cultural contexts of each language. Make appropriate adjustments to ensure these elements are accurately represented, while still preserving the original tone and intent of the text and maintaining the original HTML structure."
                max_tokens = int("3072")
                section_size = int("1024")

            print(os.getenv('SYSTEM_MESSAGE'))
            sections = split_into_sections(args.filename, section_size)
            print("Manuscript loaded and split into sections...")
            corrected_manuscript = process_manuscript(args.filename, max_tokens, system_message, user_prefix)
            print("Processing manuscript completed...")
        elif args.build:
            merge_groups_and_save(args.filename)
            print("Edited manuscript saved.")

if __name__ == "__main__":
    main()
