<p align="center">
    <img src="v-chatgpt-editor.png" align="center" width="30%">
</p>
<p align="center"><h1 align="center"><code>❯ v-chatgpt-editor</code></h1></p>
<p align="center">
	<em>Transforming Manuscripts, Empowering Creativity!</em>
</p>
<p align="center">
	<!-- local repository, no metadata badges. --></p>
<p align="center">Built with the tools and technologies:</p>
<p align="center">
	<img src="https://img.shields.io/badge/.ENV-ECD53F.svg?style=flat-square&logo=dotenv&logoColor=black" alt=".ENV">
	<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=flat-square&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
</p>
<br>

## 🔗 Table of Contents

- [🔗 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
        - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
        - [☑️ Prerequisites](#️-prerequisites)
        - [⚙️ Installation](#️-installation)
        - [🔧 Configuration](#-configuration)
        - [🖥️ Command-Line Usage](#-command-line-usage)
- [🤝 Contributing](#-contributing)
- [🎗 License](#-license)

---

## 📍 Overview

This project streamlines the editing and translation of DOCX manuscripts, addressing the challenges of document management and content refinement. Key features include flexible API integration, section-based editing, and seamless output formatting. Ideal for writers, editors, and translators, it enhances productivity while preserving the author's voice and style.

---

## 👾 Features

- **API Integration** – `app/api.py` manages requests to OpenAI services.
- **DOCX Processing** – `app/docx_handler.py` splits manuscripts, applies edits, and rebuilds documents.
- **Command Interface** – `app/main.py` exposes `edit`, `translate`, `build`, and `cleanup` commands.

---

## 📁 Project Structure

```sh
└── /
    ├── README.md
    ├── IMPROVEMENTS.md
    ├── app
    │   ├── api.py
    │   ├── docx_handler.py
    │   ├── main.py
    │   ├── validate_improvements.py
    │   ├── requirements.txt
    │   ├── run.sh
    │   ├── input/
    │   ├── output/
    │   └── .env (user-provided)
    └── v-chatgpt-editor.png
```


### 📂 Project Index
<details open>
  <summary><b><code>/</code></b></summary>
  <blockquote>
    <table>
      <tr>
        <td><b><a href='/IMPROVEMENTS.md'>IMPROVEMENTS.md</a></b></td>
        <td>Summary of code quality improvements and validation steps.</td>
      </tr>
    </table>
  </blockquote>
  <details>
    <summary><b>app</b></summary>
    <blockquote>
      <table>
        <tr>
          <td><b><a href='/app/api.py'>api.py</a></b></td>
          <td>OpenAI API utilities.</td>
        </tr>
        <tr>
          <td><b><a href='/app/docx_handler.py'>docx_handler.py</a></b></td>
          <td>DOCX splitting and merging helpers.</td>
        </tr>
        <tr>
          <td><b><a href='/app/main.py'>main.py</a></b></td>
          <td>CLI entry point.</td>
        </tr>
        <tr>
          <td><b><a href='/app/validate_improvements.py'>validate_improvements.py</a></b></td>
          <td>Internal validation checks.</td>
        </tr>
        <tr>
          <td><b><a href='/app/input/'>input/</a></b></td>
          <td>Source manuscripts.</td>
        </tr>
        <tr>
          <td><b><a href='/app/output/'>output/</a></b></td>
          <td>Processed documents.</td>
        </tr>
        <tr>
          <td><b><a href='/app/requirements.txt'>requirements.txt</a></b></td>
          <td>Project dependencies.</td>
        </tr>
        <tr>
          <td><b><a href='/app/run.sh'>run.sh</a></b></td>
          <td>Interactive helper script.</td>
        </tr>
        <tr>
          <td><code>.env</code></td>
          <td>User-provided environment variables.</td>
        </tr>
      </table>
    </blockquote>
  </details>
</details>

---

## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with `v-chatgpt-editor`, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Pip

### ⚙️ Installation

To get started with `v-chatgpt-editor`:

1. Clone the repository:

   ```sh
   ❯ git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```sh
   ❯ cd v-chatgpt-editor
   ```

3. Run the setup script from the repository root to install dependencies and start the app:

   ```sh
   ❯ ./app/run.sh
   ```

   The script will automatically install dependencies, and guide you through selecting options such as editing or translating documents.

   > 💡 **Smoke test:** Running `./app/run.sh` from the project root confirms the helper script can locate its resources regardless of your current directory.

### 🔧 Configuration

Create a `.env` file in `app/` with the following variables:

```env
OPENAI_API_KEY=<required>
OPENAI_PROJECT_ID=<optional project id>
OPENAI_ORG=<optional organization>
MODEL=gpt-4o-mini
OUTPUT_DIR=output
```

This file is user-provided and should not be committed to version control.

### 🖥️ Command-Line Usage

Run the application directly:

```sh
python3 app/main.py edit path/to/file.docx
python3 app/main.py translate path/to/file.docx
python3 app/main.py build path/to/file.docx
python3 app/main.py cleanup
```

Alternatively, use the interactive helper script:

```sh
./app/run.sh
```

---

## 🤝 Contributing

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for a summary of recent code quality improvements and validation steps. Run `python3 app/validate_improvements.py` to perform internal checks before committing changes.

---

## 🎗 License

This project is protected under the [MIT License](https://github.com/djav1985/v-chatgpt-editor/blob/main/LICENSE) License.

---