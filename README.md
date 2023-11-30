# v-openai-editor

This is a Python application for correcting DOCX format manuscripts. It provides features for splitting, processing, and merging manuscript sections while preserving formatting, headers, paragraphs, and more.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed
- [pip](https://pip.pypa.io/en/stable/installation/) package manager
- [virtualenv](https://pypi.org/project/virtualenv/) installed (optional but recommended)

## Installation

1. Clone the repository:

   \```bash
   git clone https://github.com/your-username/manuscript-editor.git
   cd manuscript-editor
   \```

2. Create a virtual environment (optional but recommended):

   \```bash
   python3 -m venv venv
   source venv/bin/activate
   \```

3. Install the project's Python dependencies from the requirements.txt file:

   \```bash
   pip install -r requirements.txt
   \```

## Usage

You can use the following command-line arguments to run the application:

- `--filename`: Provide the path to your DOCX file.
- `--build`: Flag to trigger building the edited manuscript.

Here's an example of how to use the application:

   \```bash
   python main.py --filename path/to/your/manuscript.docx --build
   \```

## Features

- Split into Sections: The application can split a DOCX manuscript into sections and create .old files for each section.
- Process Manuscript: It processes the manuscript by sending sections from .old files to OpenAI for correction and creates .new files.
- Merge and Save: The corrected texts from .new files are merged while preserving formatting, headers, paragraphs, and more. The edited manuscript is saved as a new DOCX file.

## Configuration

You can configure environment variables in a .env file for controlling aspects like the maximum tokens per section, output directory, OpenAI API key, and more.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

This project utilizes the OpenAI API.
"""