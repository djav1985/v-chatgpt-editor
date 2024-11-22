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
	- [🤖 Usage](#-usage)
- [🎗 License](#-license)

---

## 📍 Overview

This project streamlines the editing and translation of DOCX manuscripts, addressing the challenges of document management and content refinement. Key features include flexible API integration, section-based editing, and seamless output formatting. Ideal for writers, editors, and translators, it enhances productivity while preserving the author's voice and style.

---

## 👾 Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Architecture**  | <ul><li>Utilizes a modular architecture with components like `app/api.py` for API interactions and `app/docx_handler.py` for document processing.</li><li>Configuration management is handled through the `.env` file, ensuring flexibility and security in environment variable management.</li><li>Integrates various functionalities such as editing, translating, and building documents through `app/main.py`, streamlining the manuscript management workflow.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Follows best practices in Python coding standards, enhancing readability and maintainability.</li><li>Utilizes a structured approach to separate concerns across different modules, such as document handling and API communication.</li><li>Includes a `requirements.txt` file that clearly defines dependencies, promoting consistency across environments.</li></ul> |
| 📄 | **Documentation** | <ul><li>Comprehensive documentation is provided, including installation and usage commands for both `<pip>`.</li><li>Code comments and module docstrings enhance understanding of functionality and usage.</li><li>Documentation covers essential aspects like configuration management and command-line functionalities.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with the `<OpenAI API>` for dynamic content generation based on user input.</li><li>Supports external services through environment variables defined in the `.env` file.</li><li>Facilitates document processing by integrating with libraries for natural language processing and web scraping.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Each component is designed to handle specific tasks, such as `app/docx_handler.py` for document manipulation and `app/api.py` for API interactions.</li><li>Encourages reusability of code across different parts of the application.</li><li>Modular design allows for easier testing and debugging of individual components.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Optimized for handling large DOCX files efficiently through chunk processing in `app/docx_handler.py`.</li><li>Utilizes asynchronous API calls to improve responsiveness during content generation.</li><li>Performance considerations are integrated into the architecture to ensure smooth user experience.</li></ul> |
| 🛡️ | **Security**      | <ul><li>Environment variables are managed securely through the `.env` file, protecting sensitive information like API keys.</li><li>Code practices are in place to prevent common vulnerabilities in API interactions.</li><li>Regular updates to dependencies in `requirements.txt` help mitigate security risks.</li></ul> |

---

## 📁 Project Structure

```sh
└── /
    ├── README.md
    ├── app
    │   ├── .env
    │   ├── api.py
    │   ├── docx_handler.py
    │   ├── main.py
    │   ├── requirements.txt
    │   └── run.sh
    └── repo.png
```


### 📂 Project Index
<details open>
	<summary><b><code>/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			</table>
		</blockquote>
	</details>
	<details> <!-- app Submodule -->
		<summary><b>app</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='/app/.env'>.env</a></b></td>
				<td>- Configuration management is facilitated through the .env file, which defines essential environment variables for the project<br>- It specifies the API key for external services, the model to be utilized, and the directory for output files<br>- This setup ensures that the application can operate seamlessly across different environments while maintaining flexibility and security in handling sensitive information.</td>
			</tr>
			<tr>
				<td><b><a href='/app/api.py'>api.py</a></b></td>
				<td>- Facilitates communication with the OpenAI API by preparing user messages and handling responses<br>- It retrieves necessary configurations from environment variables, ensuring flexibility in API interactions<br>- This functionality is integral to the project, enabling dynamic content generation based on user input and enhancing the overall user experience within the application.</td>
			</tr>
			<tr>
				<td><b><a href='/app/docx_handler.py'>docx_handler.py</a></b></td>
				<td>- Facilitates the processing of DOCX manuscripts by splitting them into manageable sections, correcting content through an API, and merging the results into a final document<br>- It enhances document formatting and style retention while ensuring that the output is organized and accessible<br>- This functionality is integral to the overall architecture, enabling efficient manuscript editing and improving the quality of the final deliverables.</td>
			</tr>
			<tr>
				<td><b><a href='/app/main.py'>main.py</a></b></td>
				<td>- Facilitates the processing of DOCX manuscript files by providing command-line functionalities for editing, translating, and building final documents<br>- It allows users to split manuscripts into sections for focused editing or translation, ensuring adherence to specific guidelines while preserving the author's voice<br>- The integration with other components in the codebase enhances the overall manuscript management workflow, streamlining the editing and translation processes.</td>
			</tr>
			<tr>
				<td><b><a href='/app/requirements.txt'>requirements.txt</a></b></td>
				<td>- Defines essential dependencies for the project, enabling functionalities such as command-line argument parsing, document manipulation, environment variable management, web scraping, and natural language processing<br>- These libraries collectively support the overall architecture by facilitating user interaction, data handling, and integration with external services, thereby enhancing the project's capability to deliver robust and dynamic features.</td>
			</tr>
			<tr>
				<td><b><a href='/app/run.sh'>run.sh</a></b></td>
				<td>- Facilitates user interaction for managing files within the project, allowing selection of input files and configuration of processing options such as editing, translating, or building<br>- It sets up a Python virtual environment, executes the appropriate scripts based on user choices, and provides a cleanup option to delete contents from specified directories<br>- This enhances the overall usability and organization of the codebase.</td>
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

3. Run the setup script to install dependencies and start the app:

   ```sh
   ❯ ./run.sh
   ```

   The script will automatically install dependencies, and guide you through selecting options such as editing or translating documents.

### 🤖 Usage

To run the application, simply use:

```sh
❯ ./run.sh
```

The script will help you choose which file to work on, and whether you want to edit or translate, making the process straightforward and interactive.

---

## 🎗 License

This project is protected under the [MIT License](https://github.com/djav1985/v-chatgpt-editor/blob/main/LICENSE) License.

---