<div id="top">

<div align="center">

<img src="v-chatgpt-editor.png" width="60%" alt="v-chatgpt-editor logo">

# V-CHATGPT-EDITOR

<em>Careful Manuscript Editing and Translation, Powered by OpenAI</em>

<img src="https://img.shields.io/github/license/djav1985/v-chatgpt-editor?style=flat-square&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/djav1985/v-chatgpt-editor?style=flat-square&logo=git&logoColor=white&color=0080ff" alt="last commit">
<img src="https://img.shields.io/github/languages/top/djav1985/v-chatgpt-editor?style=flat-square&color=0080ff" alt="top language">

<em>Built with Python, DOCX tooling, and the OpenAI API</em>

</div>

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Configuration](#configuration)
6. [Command-Line Usage](#command-line-usage)
7. [Tests](#tests)
8. [License](#license)

---

## Overview

V-ChatGPT-Editor is a command-line tool for editing and translating DOCX manuscripts. It divides documents into paragraph-preserving sections, sends those sections to OpenAI for processing, and rebuilds a formatted DOCX file. Intermediate sections are retained so processing can be resumed or the final document rebuilt separately.

---

## Features

| Component | Details |
| :--- | :--- |
| **Editing and translation** | Edit manuscripts with minimal changes or translate them into a selected language. |
| **DOCX processing** | Split and merge documents while preserving paragraph formatting and markup. |
| **Section sizing** | Set a model-token budget per section; oversized paragraphs remain intact. |
| **OpenAI integration** | Use the Responses API with configurable model, organization, and project settings. |
| **Resumable workflow** | Keep intermediate section files under `app/tmp/` and build completed DOCX files from them. |
| **Concurrency** | Configure the maximum number of sections processed concurrently. |
| **Testing** | Run the standard-library `unittest` suite in `tests/`. |

---

## Project Structure

```text
v-chatgpt-editor/
├── app/
│   ├── api.py              # OpenAI client and requests
│   ├── docx_handler.py     # DOCX splitting, processing, and merging
│   ├── docx_markup.py      # Paragraph markup serialization and restoration
│   ├── main.py             # Command-line entry point
│   ├── token_count.py      # Model token counting
│   ├── requirements.txt    # Python dependencies
│   ├── run.sh              # Interactive setup and edit/translate workflow
│   ├── .env                # Local configuration; create this file yourself
│   ├── input/              # Source DOCX files
│   ├── output/             # Completed DOCX files
│   └── tmp/                # Intermediate sections and processing state
├── tests/                  # unittest test suite
├── LICENSE
└── README.md
```

---

## Getting Started

### Requirements

- Python 3
- Bash for the interactive script (use Git Bash or WSL on Windows)
- An OpenAI API key for editing and translation

### Interactive Setup

Run the helper from the repository root:

```sh
bash app/run.sh
```

The script changes to the `app/` directory, so it can be launched from the repository root or another working directory. It then:

1. Creates `app/venv/` if the virtual environment is missing or incomplete.
2. Installs or updates packages from `app/requirements.txt` and activates the environment.
3. Prompts you to select **Edit** or **Translate**.
4. Lists `.docx` files in `app/input/` and prompts you to choose one. It exits if none are found or the file selection is invalid.
5. Prompts for the maximum token budget per section: `256`, `512`, `1024`, or `2048`. An invalid choice uses `256`. A paragraph larger than the selected budget is kept whole and can exceed the budget.
6. For translation, prompts for the target language.
7. Calls `main.py` with the selected action and options. Intermediate processing files are stored under `app/tmp/`; completed documents go to the configured output directory (default: `app/output/`).

On Windows, run the helper from Git Bash or WSL. On normal completion, the script deactivates its virtual environment.

---

## Configuration

Create `app/.env` with the settings you need:

```env
OPENAI_API_KEY=your-api-key
OPENAI_PROJECT_ID=
OPENAI_ORG=
MODEL=gpt-5-mini
MAX_CONCURRENT_SECTIONS=1
OUTPUT_DIR=./output
```

`OPENAI_API_KEY` is required for edit and translate commands. `MODEL` defaults to `gpt-5-mini`, `MAX_CONCURRENT_SECTIONS` defaults to `1`, and `OUTPUT_DIR` defaults to `./output`. Keep `app/.env` private and do not commit API credentials.

When running Python commands directly, run them from `app/` so `.env` is discovered and relative paths resolve there.

---

## Command-Line Usage

After installing the dependencies, run commands from `app/`:

```sh
python main.py edit input/manuscript.docx 512
python main.py translate input/manuscript.docx French 512
python main.py build input/manuscript.docx --edited
python main.py build input/manuscript.docx --language French
```

The `build` command rebuilds a document from existing intermediate sections and does not require an API key. Edit and translate commands build their output when processing completes. The interactive workflow is also available from the repository root with `bash app/run.sh`.

---

## Tests

Install the dependencies listed in `app/requirements.txt`, then run from the repository root:

```sh
python -m unittest discover -s tests -v
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

<div align="right"><a href="#top">Back to top</a></div>