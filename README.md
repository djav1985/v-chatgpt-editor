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

From the repository root, run:

```sh
bash app/run.sh
```

The script creates a virtual environment under `app/`, installs dependencies, and prompts you to choose an action, a DOCX file from `app/input/`, and a section token budget. Translation also prompts for a target language.

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