from pathlib import Path

from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file


repo = Path(__file__).resolve().parent
# repo = Path(r"path\to\repo\root") # Replace with this line for other repositories

# Optional: extra style/context file for LLM
extra_context_file = repo / "readme_style_context.html"  # rename if you used a different filename

# Step 1 — build query
query_cfg = {
    "repo_root": repo,
    "out_dir": repo / "doc_queries",
    "snippet_max_bytes_per_file": 5_000,
    "include_snippets": True,
    "snippet_max_files": 12,
    "tree_max_lines": 500,
}
query_path = generate_doc_query_bundle(**query_cfg)
print("Query built:", query_path)

# Step 2 — generate README from query (with optional extra context)
readme_path = generate_readme_from_query_file(
    query_path,
    extra_context_path=extra_context_file if extra_context_file.exists() else None,
)
print("README generated:", readme_path)
