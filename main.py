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

# Config
cfg = {
    "repo_root": repo, # The path or url to the repository
    "generated_root": generated_root,
    "snippet_max_bytes_per_file": 20_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
    "query_gemini": True
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