# v-chatgpt-editor

A command-line tool for editing and translating DOCX manuscripts with OpenAI. It splits documents into paragraph-preserving sections, processes those sections, and builds a formatted DOCX output.

## Features

- Edit or translate DOCX manuscripts while preserving document formatting.
- Set a token budget for each section; oversized paragraphs remain intact.
- Resume section processing and build a final document from saved intermediate files.
- Configure the OpenAI model, output directory, and section concurrency through environment variables.

## Project layout

```text
.
├── app/
│   ├── api.py              # OpenAI client and requests
│   ├── docx_handler.py     # Split, process, and merge DOCX files
│   ├── docx_markup.py     # Serialize and restore formatted paragraphs
│   ├── main.py             # CLI entry point
│   ├── token_count.py      # Model token counting
│   ├── requirements.txt
│   ├── run.sh              # Interactive setup and edit/translate workflow
│   ├── input/              # Source DOCX files
│   ├── output/             # Completed DOCX files
│   └── tmp/                # Intermediate sections and processing state
├── tests/                  # unittest test suite
├── LICENSE
└── README.md
```

The interactive script creates `app/venv` and installs dependencies from `app/requirements.txt`. Keep API credentials in `app/.env`; do not commit that file.

## Requirements

- Python 3
- Bash (for the interactive script; on Windows, use Git Bash or WSL)
- An OpenAI API key for edit and translate operations

## Setup and interactive use

From the repository root, run:

```sh
bash app/run.sh
```

The script installs dependencies in its virtual environment and prompts you to choose edit or translate, a DOCX file from `app/input/`, and the section token budget. Translation also prompts for a target language.

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

`OPENAI_API_KEY` is required for editing and translation. `MODEL` defaults to `gpt-5-mini`, `MAX_CONCURRENT_SECTIONS` defaults to `1`, and `OUTPUT_DIR` defaults to `./output`. When running commands directly, run them from `app/` so `app/.env` is loaded and these relative paths resolve as expected.

## Command-line use

Install dependencies (or run the interactive script once), then from `app/`:

```sh
python main.py edit input/manuscript.docx 512
python main.py translate input/manuscript.docx French 512
python main.py build input/manuscript.docx --edited
python main.py build input/manuscript.docx --language French
```

The `build` command rebuilds a document from existing intermediate sections; it does not require an OpenAI API key. Edit and translate commands build their output when processing completes.

## Tests

Install the app requirements, then run from the repository root:

```sh
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).