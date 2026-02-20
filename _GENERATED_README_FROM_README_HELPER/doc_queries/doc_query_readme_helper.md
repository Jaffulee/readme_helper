TASK:
Write a high-quality README.md for this repository using ONLY the context below.

RULES:
- Output only README.md markdown content (no preamble, no analysis).
- Do not invent commands, dependencies, or features not supported by the context.
- If an existing README is present, assess whether it is high quality, and improve it rather than rewriting unnecessarily if it is high quality, otherwise rewrite it.
- Use clear sections: Overview, Features, Setup, Usage, Project Structure, Notes/Design, Contributing (if relevant).

CONTEXT: REPO TREE (git-respecting, compact)
```text
_GENERATED_README_FROM_README_HELPER/
  doc_queries/
    doc_query_readme_helper.md
  generated_readmes/
    README_readme_helper.md
.gitignore
README.md
generate_readme_from_query.py
generate_readme_query.py
main.py
readme_style_context.html
requirements.txt
```

CONTEXT: FILE LIST (tracked + untracked, excluding ignored)
```text
.gitignore
_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_readme_helper.md
_GENERATED_README_FROM_README_HELPER/generated_readmes/README_readme_helper.md
generate_readme_from_query.py
generate_readme_query.py
main.py
README.md
readme_style_context.html
requirements.txt
```

CONTEXT: EXISTING README (README.md)
```md
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

4.  **Install Git (if not already present)**:
    The tool uses the `git` command-line utility to list repository files and build the file tree. Make sure Git is installed and accessible in your system's PATH.

---

## Usage

The `main.py` script orchestrates the two primary steps: generating the repository context query and then generating the README from that query.

1.  **Generate the doc query file**:
    The `generate_doc_query_bundle` function (from `generate_readme_query.py`) scans a specified repository and creates a markdown file containing all the gathered context.

2.  **Generate README from the query file**:
    The `generate_readme_from_query_file` function (from `generate_readme_from_query.py`) takes the query file, sends it to the Gemini API, and writes the LLM's response. An optional `extra_context_path` can be provided to further guide the LLM.

Here's how to run the process using `main.py`:

```python
# main.py

from pathlib import Path
from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file

# Define the root of the repository you want to document
# (Replace with the actual path to your target repository)
repo_to_document = Path("path/to/your/target/repository")

# Optional: extra style/context file for LLM.
# This file (e.g., readme_style_context.html) provides additional instructions
# to the LLM on how to format or structure the README.
extra_context_file = Path(__file__).resolve().parent / "readme_style_context.html"

# 1) Generate the doc query file inside the repo_to_document's 'doc_queries' folder
query_cfg = {
    "repo_root": repo_to_document,
    "out_dir": repo_to_document / "_GENERATED_README_FROM_README_HELPER" / "doc_queries",
    "snippet_max_bytes_per_file": 20_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
}
query_path = generate_doc_query_bundle(**query_cfg)
print(f"Wrote query: {query_path}")

# 2) Generate README from that query file
# Use generate_readme_from_query_file directly or via generate_readme_from_query_config
readme_cfg = {
    "input_path": query_path,
    "output_root": repo_to_document, # Output to the repo root to overwrite its README.md
    "model": "gemini-2.5-flash",
    "extra_context_path": extra_context_file if extra_context_file.exists() else None,
}
# Using the wrapper for dictionary config:
# readme_path = generate_readme_from_query_config(readme_cfg)
# Or direct call:
readme_path = generate_readme_from_query_file(
    input_path=readme_cfg["input_path"],
    output_root=readme_cfg["output_root"],
    model=readme_cfg["model"],
    extra_context_path=readme_cfg["extra_context_path"],
)
print(f"Wrote README: {readme_path}")
```

To run this, modify the `repo_to_document` variable in `main.py` to point to the repository for which you want to generate a README, and then execute:

```bash
python main.py
```

This will first create a query markdown file (e.g., `_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_my_repo.md`) and then use that file to generate or update the `README.md` in your target repository. If `output_root` is not specified in `generate_readme_from_query_file`, the generated README will be placed in `<repo_to_document>/_GENERATED_README_FROM_README_HELPER/generated_readmes/README_<repo_name>.md`.

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
```

CONTEXT: SELECTED SNIPPETS (sampled)
### main.py
```text
from pathlib import Path

from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file

# repo = Path(r"path\to\repo\root")
repo = Path(__file__).resolve().parent

generated_root = repo / "_GENERATED_README_FROM_README_HELPER"
doc_queries_dir = generated_root / "doc_queries"

# Optional: extra style/context file
extra_context_file = repo / "readme_style_context.html"

# Step 1 — build query (write into isolated folder)
query_cfg = {
    "repo_root": repo,
    "out_dir": doc_queries_dir,
    "snippet_max_bytes_per_file": 20_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
}
query_path = generate_doc_query_bundle(**query_cfg)
print("Query built:", query_path)

# Step 2 — generate README from query (writes into isolated folder)
readme_path = generate_readme_from_query_file(
    query_path,
    extra_context_path=extra_context_file if extra_context_file.exists() else None,
)
print("README generated:", readme_path)

```

### generate_readme_from_query.py
```text
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from google import genai


def _read_text_with_bom_fallback(path: Path) -> str:
    """
    Read a text file safely (handles BOM).
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def generate_readme_from_query_file(
    input_path: Path,
    *,
    model: str = "gemini-2.5-flash",
    env_path: Optional[Path] = None,
    api_key_env_var: str = "GEMINI_API_KEY",
    output_root: Optional[Path] = None,
    extra_context_path: Optional[Path] = None,
) -> Path:
    """
    Generate README from a doc-query file using Gemini.

    Default output location:
        <target_repo>/_GENERATED_README_FROM_README_HELPER/generated_readmes/README_<repo_name>.md

    Optional:
        extra_context_path — additional text appended to the query.
    """
    input_path = input_path.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Query file not found: {input_path}")

    # Infer target repo root:
    # <repo>/_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_*.md
    # or legacy: <repo>/doc_queries/doc_query_*.md
    # We take parent.parent as the folder containing doc_queries.
    # If doc_queries is inside _GENERATED_README_FROM_README_HELPER, repo_root becomes that folder,
    # so we step up one more to get the true repo.
    doc_queries_parent = input_path.parent.parent  # folder containing doc_queries
    if doc_queries_parent.name == "_GENERATED_README_FROM_README_HELPER":
        repo_root = doc_queries_parent.parent
        generated_root = doc_queries_parent
    else:
        repo_root = doc_queries_parent
        generated_root = repo_root / "_GENERATED_README_FROM_README_HELPER"

    repo_name = repo_root.name

    # Output folder
    if output_root is None:
        output_root = generated_root / "generated_readmes"

    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    output_path = output_root / f"README_{repo_name}.md"

    # Load environment variables
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    api_key = os.getenv(api_key_env_var)
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)

    # Read main query file
    query_text = _read_text_with_bom_fallback(input_path)

    # Optional extra context file
    extra_text = ""
    if extra_context_path:
        extra_context_path = extra_context_path.resolve()
        if not extra_context_path.exists():
            raise FileNotFoundError(f"Extra context file not found: {extra_context_path}")
        extra_text = _read_text_with_bom_fallback(extra_context_path)

    # Final message to Gemini (swap markdown->HTML here if desired)
    message = (
        "You will be given a repository documentation prompt.\n"
        "Generate a complete high-quality README.\n"
        "Output ONLY markdown. No explanations.\n\n"
        + query_text
    )

    if extra_text:
        message += "\n\nADDITIONAL CONTEXT:\n" + extra_text

    resp = client.models.generate_content(
        model=model,
        contents=message,
    )

    text = resp.text
    if not text or not text.strip():
        raise RuntimeError("Empty response from Gemini")

    output_path.write_text(text, encoding="utf-8")
    return output_path


def generate_readme_from_query_config(config: Dict) -> Path:
    """
    Dict wrapper so you can call with **cfg
    """
    return generate_readme_from_query_file(**config)

```

### _GENERATED_README_FROM_README_HELPER/generated_readmes/README_readme_helper.md
```text
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

4.  **Install Git (if not already present)**:
    The tool uses the `git` command-line utility to list repository files and build the file tree. Make sure Git is installed and accessible in your system's PATH.

---

## Usage

The `main.py` script orchestrates the two primary steps: generating the repository context query and then generating the README from that query.

1.  **Generate the doc query file**:
    The `generate_doc_query_bundle` function (from `generate_readme_query.py`) scans a specified repository and creates a markdown file containing all the gathered context.

2.  **Generate README from the query file**:
    The `generate_readme_from_query_file` function (from `generate_readme_from_query.py`) takes the query file, sends it to the Gemini API, and writes the LLM's response. An optional `extra_context_path` can be provided to further guide the LLM.

Here's how to run the process using `main.py`:

```python
# main.py

from pathlib import Path
from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file

# Define the root of the repository you want to document
# (Replace with the actual path to your target repository)
repo_to_document = Path("path/to/your/target/repository")

# Optional: extra style/context file for LLM.
# This file (e.g., readme_style_context.html) provides additional instructions
# to the LLM on how to format or structure the README.
extra_context_file = Path(__file__).resolve().parent / "readme_style_context.html"

# 1) Generate the doc query file inside the repo_to_document's 'doc_queries' folder
query_cfg = {
    "repo_root": repo_to_document,
    "out_dir": repo_to_document / "_GENERATED_README_FROM_README_HELPER" / "doc_queries",
    "snippet_max_bytes_per_file": 20_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
}
query_path = generate_doc_query_bundle(**query_cfg)
print(f"Wrote query: {query_path}")

# 2) Generate README from that query file
# Use generate_readme_from_query_file directly or via generate_readme_from_query_config
readme_cfg = {
    "input_path": query_path,
    "output_root": repo_to_document, # Output to the repo root to overwrite its README.md
    "model": "gemini-2.5-flash",
    "extra_context_path": extra_context_file if extra_context_file.exists() else None,
}
# Using the wrapper for dictionary config:
# readme_path = generate_readme_from_query_config(readme_cfg)
# Or direct call:
readme_path = generate_readme_from_query_file(
    input_path=readme_cfg["input_path"],
    output_root=readme_cfg["output_root"],
    model=readme_cfg["model"],
    extra_context_path=readme_cfg["extra_context_path"],
)
print(f"Wrote README: {readme_path}")
```

To run this, modify the `repo_to_document` variable in `main.py` to point to the repository for which you want to generate a README, and then execute:

```bash
python main.py
```

This will first create a query markdown file (e.g., `_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_my_repo.md`) and then use that file to generate or update the `README.md` in your target repository. If `output_root` is not specified in `generate_readme_from_query_file`, the generated README will be placed in `<repo_to_document>/_GENERATED_README_FROM_README_HELPER/generated_readmes/README_<repo_name>.md`.

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
```

### generate_readme_query.py
```text
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class GitFileListing:
    """
    Result of querying git for the files considered part of the working set
    (tracked + untracked, excluding ignored via git's exclude-standard rules).
    """
    files: List[Path]
    is_git_repo: bool
    git_error: Optional[str] = None


def _run(cmd: Sequence[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        check=False,
    )


def get_git_included_files(repo_root: Path) -> GitFileListing:
    """
    Uses git to list all tracked + untracked files, excluding ignored files.

    Equivalent conceptually to:
      git ls-files --cached --others --exclude-standard

    This respects:
    - all .gitignore files (including nested)
    - .git/info/exclude
    - global gitignore settings
    """
    repo_root = repo_root.resolve()

    probe = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    if probe.returncode != 0:
        return GitFileListing(
            files=[],
            is_git_repo=False,
            git_error=probe.stderr.decode(errors="replace").strip() or "Not a git repository.",
        )

    proc = _run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=repo_root)
    if proc.returncode != 0:
        return GitFileListing(
            files=[],
            is_git_repo=True,
            git_error=proc.stderr.decode(errors="replace").strip() or "git ls-files failed.",
        )

    parts = [p for p in proc.stdout.split(b"\x00") if p]
    files = [repo_root / Path(p.decode("utf-8", errors="replace")) for p in parts]
    files = [p for p in files if p.is_file()]

    return GitFileListing(files=files, is_git_repo=True)


def is_likely_binary(path: Path) -> bool:
    """
    Heuristic to avoid embedding binary content into the query bundle.
    """
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in chunk


def read_text_file_safe(path: Path, max_bytes: int) -> Optional[str]:
    """
    Reads a file as text (best-effort), truncating to max_bytes.
    Handles common BOM encodings (UTF-8/UTF-16).
    Returns None if the file can't be reasonably treated as text.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None

    if len(data) > max_bytes:
        data = data[:max_bytes] + b"\n\n... (truncated)\n"

    # BOM sniff (most reliable for Windows-saved files)
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        try:
            return data.decode("utf-16")
        except UnicodeDecodeError:
            pass
    if data.startswith(b"\xef\xbb\xbf"):
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            pass

    # Normal decode attempts
    for enc in ("utf-8", "utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def build_compact_tree(repo_root: Path, files: List[Path], max_lines: int) -> str:
    """
    Builds a compact, git-respecting tree representation from the file list.
    """
    tree: dict = {}
    for f in files:
        rel = f.relative_to(repo_root)
        node = tree
        for part in rel.parts[:-1]:
            node = node.setdefault(part, {})
        node.setdefault("__files__", []).append(rel.parts[-1])

    lines: List[str] = []

    def walk(node: dict, prefix: str = "") -> None:
        dirs = sorted([k for k in node.keys() if k not in ("__files__",)])
        files_here = sorted(node.get("__files__", []))

        for d in dirs:
            lines.append(f"{prefix}{d}/")
            walk(node[d], prefix + "  ")

        for fn in files_here:
            lines.append(f"{prefix}{fn}")

    walk(tree)

    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"... (truncated tree; {len(lines) - max_lines} more lines)"]

    return "\n".join(lines)


def pick_existing_readme(repo_root: Path, candidates: Sequence[str]) -> Optional[Path]:
    for name in candidates:
        p = repo_root / name
        if p.is_file():
            return p
    return None


def select_key_files(repo_root: Path, key_files: Sequence[str]) -> List[Path]:
    found: List[Path] = []
    for name in key_files:
        p = repo_root / name
        if p.is_file():
            found.append(p)
    return found


def select_snippet_files(
    files: List[Path],
    include_snippets: bool,
    snippet_max_files: int,
    exclude_paths: Optional[set[Path]] = None,
) -> List[Path]:
    """
    Chooses candidate files for snippet inclusion (small, text-like, common extensions).

    exclude_paths should contain resolved Paths.
    """
    if not include_snippets:
        return []

    exclude_paths = exclude_paths or set()

    exts = {".py", ".sql", ".md", ".yml", ".yaml", ".toml", ".json", ".js", ".ts", ".sh", ".ps1"}
    candidates: List[Tuple[int, Path]] = []

    for p in files:
        rp = p.resolve()
        if rp in exclude_paths:
            continue
        if p.suffix.lower() not in exts:
            continue
        if is_likely_binary(p):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        candidates.append((size, p))

    candidates.sort(key=lambda t: t[0])
    return [p for _, p in candidates[:snippet_max_files]]


def generate_doc_query_bundle(
    repo_root: Path,
    out_dir: Path,
    snippet_max_bytes_per_file: int,
    *,
    include_snippets: bool = False,
    snippet_max_files: int = 10,
    tree_max_lines: int = 400,
    max_bytes_readme: int = 250_000,
    max_bytes_key_files: int = 200_000,
    readme_candidates: Sequence[str] = ("README.md", "README.rst", "README.txt"),
    key_files: Sequence[str] = (
        "pyproject.toml",
        "requirements.txt",
        "environment.yml",
        "Pipfile",
        "poetry.lock",
        "setup.cfg",
        "setup.py",
        "package.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "package-lock.json",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        ".env.example",
        "LICENSE",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
    ),
) -> Path:
    """
    Builds a single markdown file containing the LLM query + repo structure + file list + selected file contents.

    Output filename:
      doc_query_<repo_folder_name>.md
    """
    repo_root = repo_root.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    folder_name = repo_root.name
    out_path = out_dir / f"doc_query_{folder_name}.md"

    listing = get_git_included_files(repo_root)

    rel_files = [str(p.relative_to(repo_root)).replace("\\", "/") for p in sorted(listing.files)]
    tree_str = build_compact_tree(repo_root, listing.files, max_lines=tree_max_lines) if listing.files else ""

    existing_readme = pick_existing_readme(repo_root, candidates=readme_candidates)
    selected_key_files = select_key_files(repo_root, key_files=key_files)

    # Dedupe registry: any file included anywhere must not appear again
    included_paths: set[Path] = set()

    def mark_included(p: Path) -> None:
        included_paths.add(p.resolve())

    def is_included(p: Path) -> bool:
        return p.resolve() in included_paths

    # Pre-exclude README + key files from snippet selection (and anything else you add later)
    excluded: set[Path] = set()
    if existing_readme:
        excluded.add(existing_readme.resolve())
    for kf in selected_key_files:
        excluded.add(kf.resolve())

    snippet_paths = select_snippet_files(
        files=listing.files,
        include_snippets=include_snippets,
        snippet_max_files=snippet_max_files,
        exclude_paths=excluded,
    )

    parts: List[str] = []

    parts.append(
        "\n".join(
            [
                "TASK:",
                "Write a high-quality README.md for this repository using ONLY the context below.",
                "",
                "RULES:",
                "- Output only README.md markdown content (no preamble, no analysis).",
                "- Do not invent commands, dependencies, or features not supported by the context.",
                "- If an existing README is present, improve it rather than rewriting unnecessarily.",
                "- Use clear sections: Overview, Features, Setup, Usage, Project Structure, Notes/Design, Contributing (if relevant).",
            ]
        )
    )
    parts.append("")

    parts.append("CONTEXT: REPO TREE (git-respecting, compact)")
    parts.append("```text")
    parts.append(tree_str if tree_str else "(no files found via git listing)")
    parts.append("```")
    parts.append("")

    parts.append("CONTEXT: FILE LIST (tracked + untracked, excluding ignored)")
    parts.append("```text")
    parts.append("\n".join(rel_files) if rel_files else "(no files found via git listing)")
    parts.append("```")
    parts.append("")

    if existing_readme and not is_included(existing_readme):
        txt = read_text_file_safe(existing_readme, max_bytes=max_bytes_readme) or ""
        parts.append(f"CONTEXT: EXISTING README ({existing_readme.name})")
        parts.append("```md")
        parts.append(txt)
        parts.append("```")
        parts.append("")
        mark_included(existing_readme)

    for p in selected_key_files:
        if existing_readme and p.resolve() == existing_readme.resolve():
            continue
        if is_included(p):
            continue
        if is_likely_binary(p):
            continue

        txt = read_text_file_safe(p, max_bytes=max_bytes_key_files)
        if txt is None:
            continue

        parts.append(f"CONTEXT: KEY FILE ({p.name})")
        parts.append("```text")
        parts.append(txt)
        parts.append("```")
        parts.append("")
        mark_included(p)

    if snippet_paths:
        parts.append("CONTEXT: SELECTED SNIPPETS (sampled)")
        for p in snippet_paths:
            if is_included(p):
                continue

            txt = read_text_file_safe(p, max_bytes=snippet_max_bytes_per_file)
            if txt is None:
                continue

            rel = str(p.relative_to(repo_root)).replace("\\", "/")
            parts.append(f"### {rel}")
            parts.append("```text")
            parts.append(txt)
            parts.append("```")
            parts.append("")
            mark_included(p)

    out_path.write_text("\n".join(parts), encoding="utf-8")

    if not out_path.exists():
        raise RuntimeError(f"Expected output file was not created: {out_path}")
    if out_path.stat().st_size == 0:
        raise RuntimeError(f"Output file was created but is empty: {out_path}")

    return out_path


def generate_doc_query_bundle_from_config(config: Dict) -> Path:
    """
    Convenience wrapper so you can do:
      cfg = {...}
      generate_doc_query_bundle(**cfg)
    """
    return generate_doc_query_bundle(**config)

```

### _GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_readme_helper.md
```text
TASK:
Write a high-quality README.md for this repository using ONLY the context below.

RULES:
- Output only README.md markdown content (no preamble, no analysis).
- Do not invent commands, dependencies, or features not supported by the context.
- If an existing README is present, improve it rather than rewriting unnecessarily.
- Use clear sections: Overview, Features, Setup, Usage, Project Structure, Notes/Design, Contributing (if relevant).

CONTEXT: REPO TREE (git-respecting, compact)
```text
_GENERATED_README_FROM_README_HELPER/
  doc_queries/
    doc_query_readme_helper.md
  generated_readmes/
    README_readme_helper.md
.gitignore
README.md
generate_readme_from_query.py
generate_readme_query.py
main.py
readme_style_context.html
requirements.txt
```

CONTEXT: FILE LIST (tracked + untracked, excluding ignored)
```text
.gitignore
_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_readme_helper.md
_GENERATED_README_FROM_README_HELPER/generated_readmes/README_readme_helper.md
generate_readme_from_query.py
generate_readme_query.py
main.py
README.md
readme_style_context.html
requirements.txt
```

CONTEXT: EXISTING README (README.md)
```md
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



4.  **Install Git (if not already present)**:

    The tool uses the `git` command-line utility to list repository files and build the file tree. Make sure Git is installed and accessible in your system's PATH.



---



## Usage



The `main.py` script orchestrates the two primary steps: generating the repository context query and then generating the README from that query.



1.  **Generate the doc query file**:

    The `generate_doc_query_bundle` function (from `generate_readme_query.py`) scans a specified repository and creates a markdown file containing all the gathered context.



2.  **Generate README from the query file**:

    The `generate_readme_from_query_file` function (from `generate_readme_from_query.py`) takes the query file, sends it to the Gemini API, and writes the LLM's response. An optional `extra_context_path` can be provided to further guide the LLM.



Here's how to run the process using `main.py`:



```python

# main.py



from pathlib import Path

from generate_readme_query import generate_doc_query_bundle

from generate_readme_from_query import generate_readme_from_query_file



# Define the root of the repository you want to document

# (Replace with the actual path to your target repository)

repo_to_document = Path("path/to/your/target/repository")



# Optional: extra style/context file for LLM.

# This file (e.g., readme_style_context.html) provides additional instructions

# to the LLM on how to format or structure the README.

extra_context_file = Path(__file__).resolve().parent / "readme_style_context.html"



# 1) Generate the doc query file inside the repo_to_document's 'doc_queries' folder

query_cfg = {

    "repo_root": repo_to_document,

    "out_dir": repo_to_document / "doc_queries",

    "snippet_max_bytes_per_file": 20_000,

    "include_snippets": True,

    "snippet_max_files": 12,

    "tree_max_lines": 500,

}

query_path = generate_doc_query_bundle(**query_cfg)

print(f"Wrote query: {query_path}")



# 2) Generate README from that query file

# Use generate_readme_from_query_file directly or via generate_readme_from_query_config

readme_cfg = {

    "input_path": query_path,

    "output_root": repo_to_document, # Output to the repo root to overwrite its README.md

    "model": "gemini-2.5-flash",

    "extra_context_path": extra_context_file if extra_context_file.exists() else None,

}

# Using the wrapper for dictionary config:

# readme_path = generate_readme_from_query_config(readme_cfg)

# Or direct call:

readme_path = generate_readme_from_query_file(

    input_path=readme_cfg["input_path"],

    output_root=readme_cfg["output_root"],

    model=readme_cfg["model"],

    extra_context_path=readme_cfg["extra_context_path"],

)

print(f"Wrote README: {readme_path}")

```



To run this, modify the `repo_to_document` variable in `main.py` to point to the repository for which you want to generate a README, and then execute:



```bash

python main.py

```



This will first create a query markdown file (e.g., `doc_queries/doc_query_my_repo.md`) and then use that file to generate or update the `README.md` in your target repository. If `output_root` is not specified, the generated README will be placed in `<repo_to_document>/generated_readmes/README_<repo_name>.md`.



---



## Project Structure



```text

doc_queries/

  doc_query_readme_helper.md # Example generated query bundle

generated_readmes/

  README_readme_helper.md    # Example generated README

.gitignore                   # Files/folders to ignore from git

README.md                    # This README file

generate_readme_from_query.py # Module for AI-driven README generation

generate_readme_query.py      # Module for repository context gathering

main.py                      # Orchestrates the README generation process

readme_style_context.html    # Optional file for LLM style guidance or additional context

requirements.txt             # Python dependencies

```



*   `main.py`: The entry point script that configures and executes the two main stages of README generation.

*   `generate_readme_query.py`: Contains functions to scan a repository, list files, build a compact file tree, identify key files (like `requirements.txt` or `Dockerfile`), read existing READMEs, and select code snippets. It compiles all this information into a structured markdown string, which forms the LLM's prompt.

*   `generate_readme_from_query.py`: Responsible for interfacing with the Google Gemini API. It reads the markdown query generated by `generate_readme_query.py`, sends it to the specified Gemini model, and writes the returned markdown content to the target `README.md` file. It also supports including an `extra_context_path` for additional LLM instructions.

*   `doc_queries/`: A directory intended to store the intermediate markdown query bundles generated for different repositories.

*   `generated_readmes/`: A directory to store generated READMEs when `output_root` is not explicitly set in `generate_readme_from_query_file`.

*   `readme_style_context.html`: An optional file that can be passed to `generate_readme_from_query_file` as `extra_context_path` to provide the LLM with additional styling rules or content to consider when generating the README.



---



## Notes/Design



The core design principle of this tool is to provide the LLM with a highly structured and comprehensive context about the repository it needs to document, while adhering to strict rules about the LLM's output.



The `generate_readme_query.py` module focuses on intelligent context extraction:

*   It leverages Git to ensure only relevant, non-ignored files are considered.

*   It prioritizes existing documentation (e.g., `README.md`) and common configuration files, as these often contain critical project metadata.

*   Heuristics are used to prevent binary files from being included and to truncate very large text files, balancing completeness with token limits and prompt efficiency.

*   The generated query bundle explicitly includes `TASK` and `RULES` sections to guide the LLM's behavior, ensuring the output is a high-quality `README.md` with clear sections and no extraneous content.
```

CONTEXT: SELECTED SNIPPETS (sampled)
### main.py
```text
from pathlib import Path



from generate_readme_query import generate_doc_query_bundle

from generate_readme_from_query import generate_readme_from_query_file



# repo = Path(r"path\to\repo\root")

repo = Path(__file__).resolve().parent



generated_root = repo / "_GENERATED_README_FROM_README_HELPER"

doc_queries_dir = generated_root / "doc_queries"



# Optional: extra style/context file

extra_context_file = repo / "readme_style_context.html"



# Step 1 — build query (write into isolated folder)

query_cfg = {

    "repo_root": repo,

    "out_dir": doc_queries_dir,

    "snippet_max_bytes_per_file": 20_000,

    "include_snippets": True,

    "snippet_max_files": 12,

    "tree_max_lines": 500,

}

query_path = generate_doc_query_bundle(**query_cfg)

print("Query built:", query_path)



# Step 2 — generate README from query (writes into isolated folder)

readme_path = generate_readme_from_query_file(

    query_path,

    extra_context_path=extra_context_file if extra_context_file.exists() else None,

)

print("README generated:", readme_path)


```

### generate_readme_from_query.py
```text
from __future__ import annotations



import os

from pathlib import Path

from typing import Dict, Optional



from dotenv import load_dotenv

from google import genai





def _read_text_with_bom_fallback(path: Path) -> str:

    """

    Read a text file safely (handles BOM).

    """

    try:

        return path.read_text(encoding="utf-8")

    except UnicodeDecodeError:

        return path.read_text(encoding="utf-8-sig")





def generate_readme_from_query_file(

    input_path: Path,

    *,

    model: str = "gemini-2.5-flash",

    env_path: Optional[Path] = None,

    api_key_env_var: str = "GEMINI_API_KEY",

    output_root: Optional[Path] = None,

    extra_context_path: Optional[Path] = None,

) -> Path:

    """

    Generate README from a doc-query file using Gemini.



    Default output location:

        <target_repo>/_GENERATED_README_FROM_README_HELPER/generated_readmes/README_<repo_name>.md



    Optional:

        extra_context_path — additional text appended to the query.

    """

    input_path = input_path.resolve()

    if not input_path.exists():

        raise FileNotFoundError(f"Query file not found: {input_path}")



    # Infer target repo root:

    # <repo>/_GENERATED_README_FROM_README_HELPER/doc_queries/doc_query_*.md

    # or legacy: <repo>/doc_queries/doc_query_*.md

    # We take parent.parent as the folder containing doc_queries.

    # If doc_queries is inside _GENERATED_README_FROM_README_HELPER, repo_root becomes that folder,

    # so we step up one more to get the true repo.

    doc_queries_parent = input_path.parent.parent  # folder containing doc_queries

    if doc_queries_parent.name == "_GENERATED_README_FROM_README_HELPER":

        repo_root = doc_queries_parent.parent

        generated_root = doc_queries_parent

    else:

        repo_root = doc_queries_parent

        generated_root = repo_root / "_GENERATED_README_FROM_README_HELPER"



    repo_name = repo_root.name



    # Output folder

    if output_root is None:

        output_root = generated_root / "generated_readmes"



    output_root = output_root.resolve()

    output_root.mkdir(parents=True, exist_ok=True)



    output_path = output_root / f"README_{repo_name}.md"



    # Load environment variables

    if env_path:

        load_dotenv(dotenv_path=env_path)

    else:

        load_dotenv()



    api_key = os.getenv(api_key_env_var)

    if not api_key:

        raise RuntimeError("GEMINI_API_KEY not set in .env")



    client = genai.Client(api_key=api_key)



    # Read main query file

    query_text = _read_text_with_bom_fallback(input_path)



    # Optional extra context file

    extra_text = ""

    if extra_context_path:

        extra_context_path = extra_context_path.resolve()

        if not extra_context_path.exists():

            raise FileNotFoundError(f"Extra context file not found: {extra_context_path}")

        extra_text = _read_text_with_bom_fallback(extra_context_path)



    # Final message to Gemini (swap markdown->HTML here if desired)

    message = (

        "You will be given a repository documentation prompt.\n"

        "Generate a complete high-quality README.\n"

        "Output ONLY markdown. No explanations.\n\n"

        + query_text

    )



    if extra_text:

        message += "\n\nADDITIONAL CONTEXT:\n" + extra_text



    resp = client.models.generate_content(

        model=model,

        contents=message,

    )



    text = resp.text

    if not text or not text.strip():

        raise RuntimeError("Empty response from Gemini")



    output_path.write_text(text, encoding="utf-8")

    return output_path





def generate_readme_from_query_config(config: Dict) -> Path:

    """

    Dict wrapper so you can call with **cfg

    """

    return generate_readme_from_query_file(**config)


```

### _GENERATED_README_FROM_README_HELPER/generated_readmes/README_readme_helper.md
```text
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



4.  **Install Git (if not already present)**:

    The tool uses the `git` command-line utility to list repository files and build the file tree. Make sure Git is installed and accessible in your system's PATH.



---



## Usage



The `main.py` script orchestrates the two primary steps: generating the repository context query and then generating the README from that query.



1.  **Generate the doc query file**:

    The `generate_doc_query_bundle` function (from `generate_readme_query.py`) scans a specified repository and creates a markdown file containing all the gathered context.



2.  **Generate README from the query file**:

    The `generate_readme_from_query_file` function (from `generate_readme_from_query.py`) takes

... (truncated)

```
