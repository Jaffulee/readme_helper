[Visit my website](https://jaffulee.github.io/Jaffulee/)

# readme_helper

## Overview

This repository provides a Python-based tool for automatically generating high-quality `README.md` files using a Large Language Model (LLM), specifically the Google Gemini API. It works by first systematically collecting relevant context from a given repository (file tree, file list, existing READMEs, key configuration files, and code snippets) into a structured markdown "query bundle," and then sending this bundle as a prompt to the LLM to generate the final `README.md`.

The goal is to streamline the documentation process, ensuring that READMEs are comprehensive and reflect the current state of the repository.

---

## Features

*   **AI-Powered README Generation**: Utilizes the Google Gemini API (defaulting to `gemini-2.5-flash`) to create descriptive and well-structured READMEs.
*   **Automatic Context Gathering**: Scans the target repository to collect crucial information including:
    *   A compact, git-respecting representation of the repository's file tree.
    *   A comprehensive list of all tracked and untracked files (excluding ignored files via `.gitignore`).
    *   Content of any existing `README.md` (or other specified README candidates).
    *   Content of common key configuration files (e.g., `requirements.txt`, `pyproject.toml`, `Dockerfile`).
    *   Sampled code snippets from relevant source files to provide functional context.
*   **Git-Aware File Handling**: Leverages `git ls-files` to accurately identify and list files, respecting `.gitignore` rules.
*   **Configurable Snippet Inclusion**: Allows control over whether code snippets are included, the maximum number of snippet files, and the maximum bytes per snippet.
*   **Robust File Reading**: Handles various text encodings, detects and avoids binary files, and truncates overly large files to manage token limits.
*   **Modular Design**: Separates the concerns of repository context gathering (`generate_readme_query.py`) and AI-driven README generation (`generate_readme_from_query.py`) for clarity and flexibility.
*   **Optional Extra Context**: Supports providing an additional file (e.g., `readme_style_context.html`) to guide the LLM's output style or provide further instructions beyond the gathered repository context.

---

## Setup

To get this project running, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/readme_helper.git
    cd readme_helper
    ```

2.  **Install Python Dependencies**:
    The project relies on `python-dotenv` for environment variable management and `google-genai` for interacting with the Gemini API.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The `requirements.txt` file is expected to contain `python-dotenv` and `google-genai`.)*

3.  **Set up Gemini API Key**:
    You need a Google Gemini API key. Create a `.env` file in the root of this repository (or specify a different path) and add your API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
    Ensure your API key starts with `AIza...`.

    Further instructions found in my tutorial repository [https://github.com/Jaffulee/gemini_api_template](https://github.com/Jaffulee/gemini_api_template), which I used to set up this repository!

4.  **Install Git (if not already present)**:
    The tool uses the `git` command-line utility to list repository files and build the file tree. Make sure Git is installed and accessible in your system's PATH.

---

## Usage

The `main.py` script orchestrates the two primary steps: generating the repository context query and then generating the README from that query.

1.  **Generate the doc query file**:
    The `generate_doc_query_bundle` function (from `generate_readme_query.py`) scans a specified repository and creates a markdown file containing all the gathered context.

2.  **Generate README from the query file**:
    The `generate_readme_from_query_file` function (from `generate_readme_from_query.py`) takes the query file, sends it to the Gemini API, and writes the LLM's response. An optional `extra_context_path` can be provided to further guide the LLM.

Here's how to run the process using `main.py` for *this* repository itself as an example target:

```python
# main.py

from pathlib import Path
from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file

# Define the root of the repository you want to document.
# For this example, we're documenting the readme_helper repository itself.
repo_to_document = Path(__file__).resolve().parent

generated_root = repo_to_document / "_GENERATED_README_FROM_README_HELPER"
doc_queries_dir = generated_root / "doc_queries"

# Optional: extra style/context file for LLM.
# This file (e.g., readme_style_context.html) provides additional instructions
# to the LLM on how to format or structure the README.
extra_context_file = repo_to_document / "readme_style_context.html"

# 1) Generate the doc query file inside the target repo's 'doc_queries' folder
query_cfg = {
    "repo_root": repo_to_document,
    "out_dir": doc_queries_dir,
    "snippet_max_bytes_per_file": 20_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
}
query_path = generate_doc_query_bundle(**query_cfg)
print(f"Wrote query: {query_path}")

# 2) Generate README from that query file.
# By default, the README is generated in a subfolder within _GENERATED_README_FROM_README_HELPER.
readme_path = generate_readme_from_query_file(
    input_path=query_path,
    extra_context_path=extra_context_file if extra_context_file.exists() else None,
)
print(f"Wrote README: {readme_path}")

# If you wanted to overwrite the target repository's README.md directly,
# you would explicitly set 'output_root' like this:
# readme_path_overwrite = generate_readme_from_query_file(
#     input_path=query_path,
#     output_root=repo_to_document,
#     extra_context_path=extra_context_file if extra_context_file.exists() else None,
# )
# print(f"Wrote README to overwrite: {readme_path_overwrite}")
```

To run this, execute:

```bash
python main.py
```

This will first create a query markdown file (e.g., `_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_readme_helper.md` for this repository) and then use that file to generate a new `README.md` within `_GENERATED_README_FROM_README_HELPER/generated_readmes/` in your target repository. If you wish to directly update the main `README.md` of the target repository, refer to the commented-out `output_root` example in `main.py`.

---

## Project Structure

```text
.
├── _GENERATED_README_FROM_README_HELPER/
│   ├── doc_queries/
│   │   └── doc_query_readme_helper.md # Example generated query bundle (for this repo)
│   └── generated_readmes/
│       └── README_readme_helper.md    # Example generated README (for this repo)
├── .gitignore                   # Files/folders to ignore from git
├── README.md                    # This README file
├── generate_readme_from_query.py # Module for AI-driven README generation
├── generate_readme_query.py      # Module for repository context gathering
├── main.py                      # Orchestrates the README generation process
├── readme_style_context.html    # Optional file for LLM style guidance or additional context
└── requirements.txt             # Python dependencies
```

*   `main.py`: The entry point script that configures and executes the two main stages of README generation.
*   `generate_readme_query.py`: Contains functions to scan a repository, list files, build a compact file tree, identify key files (like `requirements.txt` or `Dockerfile`), read existing READMEs, and select code snippets. It compiles all this information into a structured markdown string, which forms the LLM's prompt.
*   `generate_readme_from_query.py`: Responsible for interfacing with the Google Gemini API. It reads the markdown query generated by `generate_readme_query.py`, sends it to the specified Gemini model, and writes the returned markdown content to the target `README.md` file. It also supports including an `extra_context_path` for additional LLM instructions.
*   `_GENERATED_README_FROM_README_HELPER/`: A directory created in the target repository to hold generated assets.
*   `_GENERATED_README_FROM_README_HELPER/doc_queries/`: A subdirectory to store the intermediate markdown query bundles. When documenting an external repository, a `doc_queries` folder is typically created within the `_GENERATED_README_FROM_README_HELPER` directory inside that target repository.
*   `_GENERATED_README_FROM_README_HELPER/generated_readmes/`: A subdirectory to store generated READMEs. When `output_root` is not explicitly set in `generate_readme_from_query_file`, the output will be placed here within a `_GENERATED_README_FROM_README_HELPER` directory inside the target repository.
*   `readme_style_context.html`: An optional file that can be passed to `generate_readme_from_query_file` as `extra_context_path` to provide the LLM with additional styling rules or content to consider when generating the README.

---

## Notes/Design

The core design principle of this tool is to provide the LLM with a highly structured and comprehensive context about the repository it needs to document, while adhering to strict rules about the LLM's output.

The `generate_readme_query.py` module focuses on intelligent context extraction:
*   It leverages Git to ensure only relevant, non-ignored files are considered.
*   It prioritizes existing documentation (e.g., `README.md`) and common configuration files, as these often contain critical project metadata.
*   Heuristics are used to prevent binary files from being included and to truncate very large text files, balancing completeness with token limits and prompt efficiency.
*   The generated query bundle explicitly includes `TASK` and `RULES` sections to guide the LLM's behavior, ensuring the output is a high-quality `README.md` with clear sections and no extraneous content.