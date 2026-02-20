from pathlib import Path

from generate_readme_query import generate_doc_query_bundle, GitHubRepoURL

relative_root_base = Path(__file__).resolve().parent # Get relative root for context

# CASE 1: Local path
# repo = Path(r"full\path\to\git\repo\root")

# CASE 2: Relative path
# repo = relative_root_base 

# CASE 3: Public GitHub Repo URL
repo = GitHubRepoURL("https://github.com/Jaffulee/readme_helper") 

# Output file location, default to relative
generated_root_base = relative_root_base
generated_root = generated_root_base / "_GENERATED_README_FROM_README_HELPER"

# Optional: extra style/context file
extra_context_file = relative_root_base / "readme_style_context.html"

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
# repo_root:
#   The repository to document.
#   Accepts:
#     - Local path → Path("C:/full/path/to/repo")
#     - Relative path → Path(__file__).resolve().parent
#     - Remote GitHub repo → GitHubRepoURL("https://github.com/user/repo")
#
# generated_root:
#   Root output directory where ALL generated content will go.
#   The script will automatically create:
#     generated_root/
#       ├── doc_queries/          # LLM input query bundles
#       └── generated_readmes/    # Final README outputs
#
# include_snippets:
#   If True → include actual file contents in LLM context.
#   If False → only repo structure + file list used.
#   Usually keep True for best README quality.
#
# snippet_max_bytes_per_file:
#   Max bytes read from each file when building context.
#   Prevents massive files from flooding the prompt.
#   20_000–50_000 recommended.
#
# snippet_max_files:
#   Maximum number of files whose contents are included.
#   Files are selected in priority order:
#       1. Code/config/docs (.py, .md, .json, etc.)
#       2. Notebooks (.ipynb)
#       3. No-extension files (Dockerfile, Makefile, etc.)
#
# tree_max_lines:
#   Maximum number of lines in repo tree view.
#   Prevents extremely large repos flooding prompt.
#
# query_gemini:
#   If True → send generated query to Gemini and produce README.
#   If False → only generate the query file (for manual use).
# ---------------------------------------------------------------------

# Config
cfg = {
    "repo_root": repo,  # The path or GitHubRepoURL to the repository
    "generated_root": generated_root,  # Where outputs are written
    "include_snippets": True,  # Include file contents in LLM context
    "snippet_max_bytes_per_file": 20_000,  # Max bytes per file snippet
    "snippet_max_files": 12,  # Max number of snippet files
    "tree_max_lines": 500,  # Max repo tree size
    "query_gemini": True  # Whether to call Gemini to generate README
}

# Main script (leave unchanged)
if __name__ == "__main__":
    # Step 1 — build query
    query_path = generate_doc_query_bundle(
        repo_root=cfg["repo_root"],
        generated_root=cfg["generated_root"],
        snippet_max_bytes_per_file=cfg["snippet_max_bytes_per_file"],
        include_snippets=cfg["include_snippets"],
        snippet_max_files=cfg["snippet_max_files"],
        tree_max_lines=cfg["tree_max_lines"],
    )

    # Step 2 — optionally query Gemini
    if cfg.get("query_gemini", True):
        from generate_readme_from_query import generate_readme_from_query_file
        readme_path = generate_readme_from_query_file(
            query_path,
            extra_context_path=extra_context_file if extra_context_file.exists() else None,
        )
        print("README generated:", readme_path)
    else:
        print("Gemini querying disabled (query_gemini=False)")