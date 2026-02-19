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
