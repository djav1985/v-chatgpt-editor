# Copilot Instructions for AI Coding Agents

## Project Overview
- **Purpose:** Streamline editing and translation of DOCX manuscripts using modular Python components and OpenAI API integration.
- **Main Components:**
  - `app/api.py`: Handles API communication and retrieves config from environment variables.
  - `app/docx_handler.py`: Splits, edits, and merges DOCX files, preserving formatting and style.
  - `app/main.py`: CLI entry point for document processing workflows.
  - `.env`: Stores sensitive config (API keys, model, output directory).
  - `requirements.txt`: Defines all Python dependencies.
  - `run.sh`: Interactive script for setup, file selection, and workflow execution.

## Architecture & Data Flow
- Modular design: Each file has a clear responsibility (API, DOCX handling, CLI orchestration).
- Data flows from CLI (`main.py`/`run.sh`) → DOCX handler → API → output document.
- Environment variables (from `.env`) are used for configuration and secrets.
- Asynchronous API calls are used for performance when generating content.

## Developer Workflows
- **Setup:** Use `run.sh` to install dependencies and launch the app. It creates a Python virtual environment if needed.
- **Usage:** Always start with `run.sh` for interactive file selection and workflow (edit/translate/build).
- **Configuration:** Edit `.env` for API keys, model selection, and output directory.
- **Dependencies:** All required packages are listed in `requirements.txt`.
- **Cleanup:** Use options in `run.sh` to delete output directories/files as needed.

## Project-Specific Patterns & Conventions
- **Section-based DOCX processing:** Manuscripts are split into sections for focused editing/translation.
- **API integration:** All OpenAI API calls are routed through `api.py`, which loads config from `.env`.
- **Output management:** Results are merged and saved in the output directory specified in `.env`.
- **Security:** Sensitive info (API keys) must only be stored in `.env`, never hardcoded.
- **Error handling:** Each module is responsible for its own error management; failures in API or DOCX processing should be logged and surfaced to the CLI.

## Integration Points
- **OpenAI API:** Used for content generation and correction.
- **External libraries:** For DOCX manipulation, environment management, and NLP/web scraping (see `requirements.txt`).

## Key Files & Examples
- `app/docx_handler.py`: Example of section-based document processing and merging.
- `app/api.py`: Example of environment-driven API calls.
- `run.sh`: Example of interactive CLI workflow and environment setup.

---

**For new features or fixes:**
- Follow the modular pattern: keep API, DOCX, and CLI logic separate.
- Update `requirements.txt` for new dependencies.
- Document new workflows in `README.md` if they affect usage.
- Never hardcode secrets; always use `.env`.

---

_If any section is unclear or missing, please provide feedback for further refinement._
