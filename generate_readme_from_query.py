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

    Output location:
        <repo_root>/generated_readmes/README_<repo_name>.md

    Optional:
        extra_context_path — additional markdown appended to the query.
    """

    input_path = input_path.resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Query file not found: {input_path}")

    # Infer repo root
    # doc_queries/doc_query_repo.md → repo root
    repo_root = input_path.parent.parent
    repo_name = repo_root.name

    # Output folder
    if output_root is None:
        output_root = repo_root / "generated_readmes"

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

    # Init Gemini client
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

    # Final message to Gemini
    message = (
        "You will be given a repository documentation prompt.\n"
        "Generate a complete high-quality README.md.\n"
        "Output ONLY markdown. No explanations.\n\n"
        + query_text
    )

    if extra_text:
        message += "\n\nADDITIONAL CONTEXT:\n" + extra_text

    # Call Gemini
    resp = client.models.generate_content(
        model=model,
        contents=message,
    )

    text = resp.text
    if not text or not text.strip():
        raise RuntimeError("Empty response from Gemini")

    # Write output
    output_path.write_text(text, encoding="utf-8")

    return output_path


def generate_readme_from_query_config(config: Dict) -> Path:
    """
    Dict wrapper so you can call with **cfg
    """
    return generate_readme_from_query_file(**config)
