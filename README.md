<div>

<p><a href="https://jaffulee.github.io/Jaffulee/">Visit my website</a></p>

<h1>readme_helper</h1>

<h2>Overview</h2>
<p>
This repository provides a Python-based tool for automatically generating high-quality <code>README.md</code> files using a Large Language Model (LLM), specifically the Google Gemini API.
</p>
<p>
It works by collecting structured context from a target repository (file tree, file list, existing READMEs, key configuration files, and selected code snippets) into a markdown query bundle, then sending that bundle to Gemini to generate the final <code>README.md</code>.
</p>
<p>
The tool can document either:
</p>
<ul>
<li>a local Git repository (path on disk), or</li>
<li>a public GitHub repository (URL)</li>
</ul>
<p>
This dual input mode is intended to make it easy to use the same workflow in local development or against a remote public repo.
</p>

<hr/>

<h2>Features</h2>
<ul>
<li><strong>AI-powered README generation</strong>: Uses Google Gemini (default: <code>gemini-2.5-flash</code>) to produce structured documentation.</li>
<li><strong>Works with local repos or public GitHub URLs</strong>: Generate documentation from either a local Git repo or a public GitHub repository link.</li>
<li><strong>Automatic repository context gathering</strong>:
  <ul>
    <li>Git-aware file tree and file list</li>
    <li>Existing README detection and inclusion</li>
    <li>Key configuration file extraction (e.g., <code>requirements.txt</code>)</li>
    <li>Optional code snippet sampling for functional context</li>
  </ul>
</li>
<li><strong>Git-aware file handling</strong>: Uses <code>git ls-files</code> to respect <code>.gitignore</code> and include only relevant files.</li>
<li><strong>Configurable snippet inclusion</strong>: Control number of snippet files and max bytes per snippet.</li>
<li><strong>Robust file reading</strong>: Handles multiple encodings, avoids binary files, and truncates large files.</li>
<li><strong>Modular architecture</strong>: Separates repository scanning and LLM generation into distinct modules.</li>
<li><strong>Optional style/context injection</strong>: Supports extra context file (e.g., <code>readme_style_context.html</code>) to guide output style.</li>
</ul>

<hr/>

<h2>Setup</h2>

<h3>Repository</h3>
<p>
Project repository: <a href="https://github.com/Jaffulee/readme_helper">https://github.com/Jaffulee/readme_helper</a>
</p>

<h3>1. Clone the repository</h3>
<pre><code>git clone https://github.com/Jaffulee/readme_helper.git
cd readme_helper
</code></pre>

<h3>2. Install dependencies</h3>
<p>The project uses <code>python-dotenv</code> and <code>google-genai</code>.</p>
<pre><code>pip install -r requirements.txt
</code></pre>

<h3>3. Configure Gemini API key</h3>
<p>Create a <code>.env</code> file in the project root:</p>
<pre><code>GEMINI_API_KEY=your_gemini_api_key_here
</code></pre>
<p>The key must be accessible via environment variable <code>GEMINI_API_KEY</code>.</p>
Further instructions found in my tutorial repository
<a href="https://github.com/Jaffulee/gemini_api_template">https://github.com/Jaffulee/gemini_api_template</a>,
which I used to set up this repository!

<h3>4. Ensure Git is installed</h3>
<p>
The tool relies on the Git CLI for accurate file listing and tree generation. Git must be available in your system PATH. Instructions for Git setup can be found at <a href="https://github.com/Jaffulee/getting_started_using_github_and_python">https://github.com/Jaffulee/getting_started_using_github_and_python</a>.
</p>

<hr/>

<h2>Usage</h2>
<p>
The workflow consists of two stages:
</p>
<ol>
<li>Generate a repository context query bundle</li>
<li>Generate a README from that query using Gemini</li>
</ol>

<p>
The <code>main.py</code> script orchestrates both steps.
</p>

<h3>Example workflow</h3>
<pre><code class="language-python">from pathlib import Path
from generate_readme_query import generate_doc_query_bundle
from generate_readme_from_query import generate_readme_from_query_file

# Target repository to document
repo_to_document = Path("path/to/your/target/repository")

# Optional style/context file
extra_context_file = Path(__file__).resolve().parent / "readme_style_context.html"

# Step 1: Generate query bundle
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

# Step 2: Generate README from query
readme_path = generate_readme_from_query_file(
    input_path=query_path,
    output_root=repo_to_document,
    model="gemini-2.5-flash",
    extra_context_path=extra_context_file if extra_context_file.exists() else None,
)
print(f"Wrote README: {readme_path}")
</code></pre>

<h3>Run</h3>
<pre><code>python main.py
</code></pre>

<p>
If <code>output_root</code> is not specified, generated READMEs are written to:
</p>
<pre><code>&lt;repo&gt;/_GENERATED_README_FROM_README_HELPER/generated_readmes/README_&lt;repo_name&gt;.md
</code></pre>

<hr/>

<h2>Project Structure</h2>
<pre><code>.
├── _GENERATED_README_FROM_README_HELPER/
│   ├── doc_queries/
│   │   └── doc_query_readme_helper.md
│   └── generated_readmes/
│       └── README_readme_helper.md
├── .gitignore
├── README.md
├── generate_readme_from_query.py
├── generate_readme_query.py
├── main.py
├── readme_style_context.html
└── requirements.txt
</code></pre>

<ul>
<li><strong>main.py</strong>: Entry point orchestrating query generation and README generation.</li>
<li><strong>generate_readme_query.py</strong>: Scans repository and builds structured query bundle.</li>
<li><strong>generate_readme_from_query.py</strong>: Sends query to Gemini and writes resulting README.</li>
<li><strong>_GENERATED_README_FROM_README_HELPER/</strong>: Output directory for generated queries and READMEs.</li>
<li><strong>readme_style_context.html</strong>: Optional style or instruction context for the LLM.</li>
<li><strong>requirements.txt</strong>: Python dependencies.</li>
</ul>

<hr/>

<h2>Notes / Design</h2>
<p>
The core design principle is structured context injection: providing the LLM with a complete, deterministic representation of a repository so it can generate accurate documentation.
</p>

<h3>Context gathering strategy</h3>
<ul>
<li>Uses Git-aware file listing to avoid ignored files.</li>
<li>Prioritizes existing README and configuration files.</li>
<li>Includes optional source snippets for functional clarity.</li>
<li>Prevents binary inclusion and truncates oversized files.</li>
<li>Builds a single structured markdown prompt with explicit generation rules.</li>
</ul>

<h3>Generation pipeline</h3>
<ol>
<li>Scan repository and assemble context bundle.</li>
<li>Append optional style guidance.</li>
<li>Send structured prompt to Gemini.</li>
<li>Write returned README to output location.</li>
</ol>

<hr/>

<h2>Summary</h2>
<p>
<code>readme_helper</code> automates high-quality README creation by combining deterministic repository analysis with LLM-driven documentation generation. It supports documenting either local Git repositories or public GitHub repository URLs, using the same two-step pipeline.
</p>

</div>