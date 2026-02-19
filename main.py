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
