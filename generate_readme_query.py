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
