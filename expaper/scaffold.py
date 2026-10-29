"""Project scaffolding logic."""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import date

from rich.console import Console
from rich.tree import Tree
console = Console()

# Directory structure for new projects
PROJECT_STRUCTURE = {
    "experiments": {
        "configs": {},
        "tools": {},
        "scripts": {},
        "notebooks": {},
        "outputs": {},
        # Reviewer-facing numbered scripts + their outputs
        "analysis": {
            "results": {},
            "figures": {},
            "embeddings": {},
            "data": {},
        },
    },
    "paper": {},
    "shared": {
        "bib": {},
        "figures": {},
    },
}


def get_template_dir() -> Path:
    """Get path to bundled templates."""
    return Path(__file__).parent / "templates"


def create_directory_structure(project_path: Path, structure: dict, dry_run: bool = False) -> None:
    """Recursively create directory structure."""
    for name, substructure in structure.items():
        dir_path = project_path / name
        if dry_run:
            console.print(f"  [dim]mkdir[/dim] {dir_path}")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
        if substructure:
            create_directory_structure(dir_path, substructure, dry_run)


def copy_experimentstash_scripts(project_path: Path, dry_run: bool = False) -> None:
    """Copy experimentStash scripts to project."""
    scripts_src = get_template_dir() / "scripts"
    scripts_dst = project_path / "experiments" / "scripts"

    if not scripts_src.exists():
        console.print("[yellow]Warning: experimentStash scripts not found in templates[/yellow]")
        return

    for script in ["add_tool", "run_experiment", "snapshot_experiment"]:
        src = scripts_src / script
        dst = scripts_dst / script
        if src.exists():
            if dry_run:
                console.print(f"  [dim]copy[/dim] {script} -> experiments/scripts/")
            else:
                shutil.copy2(src, dst)
                # Make executable
                dst.chmod(dst.stat().st_mode | 0o755)


def create_meta_yaml(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Create experiments/configs/meta.yaml."""
    meta_content = f"""# Tool registry for {project_name}
tools: {{}}

experiment:
  name: {project_name}
  description: "{project_name} experiments"
  authors: []
  date_created: '{date.today().isoformat()}'

validation:
  require_commit_pins: false
  validate_configs: true
  check_dependencies: true
"""
    meta_path = project_path / "experiments" / "configs" / "meta.yaml"
    if dry_run:
        console.print(f"  [dim]write[/dim] {meta_path}")
    else:
        meta_path.write_text(meta_content)


def create_gitignore(project_path: Path, dry_run: bool = False) -> None:
    """Create comprehensive .gitignore for LaTeX + Python."""
    gitignore_src = get_template_dir() / "gitignore"
    gitignore_dst = project_path / ".gitignore"

    if gitignore_src.exists():
        if dry_run:
            console.print(f"  [dim]copy[/dim] .gitignore")
        else:
            shutil.copy2(gitignore_src, gitignore_dst)
    else:
        # Fallback: create basic gitignore
        content = """# LaTeX
*.aux
*.bbl
*.bcf
*.blg
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.toc
*.run.xml

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
dist/
build/

# Outputs
experiments/outputs/

# OS
.DS_Store
Thumbs.db
"""
        if dry_run:
            console.print(f"  [dim]write[/dim] .gitignore")
        else:
            gitignore_dst.write_text(content)


def create_readme(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Create project README."""
    content = f"""# {project_name}

Research project combining experiments and paper writing.

## Structure

```
{project_name}/
├── experiments/          # experimentStash structure
│   ├── configs/          # Hydra configs
│   ├── tools/            # Git submodules
│   ├── scripts/          # add_tool, run_experiment, snapshot_experiment
│   ├── notebooks/        # Analysis notebooks
│   └── outputs/          # Experiment outputs
├── paper/                # Overleaf-synced paper
├── shared/               # Shared resources
│   ├── bib/              # Bibliography
│   └── figures/          # Figures for paper
└── CLAUDE.md             # AI context + writing directives (tune before writing)
```

## Writing directives

`CLAUDE.md` includes a **Writing directives** section at the bottom.
**Tune it before writing**: set your target venue (NeurIPS / ICML / blog),
delete the format you're not using, and add co-author style preferences.

## Experiment Commands

```bash
# Add a tool
python3 experiments/scripts/add_tool <name> <repo_url>

# Run an experiment (direct invocation from tool directory)
cd experiments/tools/<tool>
python3 -m <module>.main --config-path=../../configs/<tool> experiment=<name>

# Snapshot for reproducibility
python3 experiments/scripts/snapshot_experiment <tool> <experiment> --tag <tag>
```

## Overleaf Sync

```bash
# Pull collaborator changes
expaper sync pull

# Push local changes
expaper sync push
```
"""
    readme_path = project_path / "README.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] README.md")
    else:
        readme_path.write_text(content)


def create_claude_md(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Create root CLAUDE.md — high-level pointers + writing directives.

    Detailed experiment conventions live in `experiments/CLAUDE.md`.
    """
    content = f"""# {project_name}

Research project combining experiments and paper writing.

## Layout

```
experiments/   experimentStash + numbered analysis scripts (see experiments/CLAUDE.md)
paper/         LaTeX paper synced with Overleaf
shared/        bib/, figures/
```

## Pointers

- **Running experiments + the numbered-script contract:** `experiments/CLAUDE.md`
- **Run log:** `experiments/EXPERIMENT_LOG.md`
- **Figure → script → CSV mapping:** `experiments/PROVENANCE.md`

## Overleaf sync

```bash
expaper sync pull   # collaborator changes
expaper sync push   # push local changes
```

## Working with this project

- Use `uv` for dependency management, never `pip install`.
- Use `python3` (not `python`) on cluster environments.
- Snapshot experiments before paper submission: `python3 experiments/scripts/snapshot_experiment`.
"""
    # Append writing directives from template
    writing_template = get_template_dir() / "writing-directive.md"
    if writing_template.exists():
        content += "\n" + writing_template.read_text()

    claude_path = project_path / "CLAUDE.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] CLAUDE.md")
    else:
        claude_path.write_text(content)


def create_experiments_claude_md(project_path: Path, dry_run: bool = False) -> None:
    """Create experiments/CLAUDE.md — the numbered-script contract.

    Tool-agnostic. Uses `<tool>` / `<module>` placeholders so the same template
    works whether the project uses manylatents, a custom tool, or no tool yet.
    """
    content = """# Experiments

This folder produces every CSV, JSON, and figure cited in the paper. **Public-facing reproduction surface** — assume a reviewer lands here cold and runs scripts in numeric order.

## CRITICAL: Use the tool's API first

Every numbered script in `analysis/` calls the upstream tool's Python API directly. **No wrappers, no local re-implementations, no helper functions.**

```python
# CORRECT — direct functional call into the tool
from <module>.api import run

result = run(data=..., algorithms=..., metrics=...)
```

```python
# WRONG — wrapping the API hides the surface the paper depends on
def run_my_thing(...):
    ...
```

```python
# WRONG — re-implementing what the tool already provides
from sklearn.neighbors import NearestNeighbors  # tool already has this, with caching
```

If the tool lacks a primitive you need, **add it upstream first** (with tests), then call it from here.

## Layout

```
experiments/
  CLAUDE.md                  # this file
  EXPERIMENT_LOG.md          # chronicle: what was run when, against which tool pin
  PROVENANCE.md              # figure → script → CSV mapping
  configs/<tool>/            # Hydra overrides for sweep launches
  tools/<tool>/              # git submodules
  scripts/                   # infrastructure (add_tool, run_experiment, snapshot_experiment)
  analysis/                  # numbered scripts — the reviewer's reading order
    _config.py               # shared paths, dataset registry, I/O helpers
    00_smoke.py              # health check: API + cfg work end-to-end
    01_*.py                  # data prep
    02_*.py                  # ...
    NN_figures.py            # all body figures
    results/                 # CSVs/JSONs land here
    figures/                 # PDF + PNG land here
    embeddings/              # cached run() outputs
    data/                    # caches
    _archive/                # exploratory scripts not on the figure-reproduction path
  outputs/                   # raw experiment outputs (gitignored)
```

## Numbered-script contract

Every `analysis/NN_*.py` follows this template:

```python
#!/usr/bin/env python
\"\"\"NN_<name>.py — <one-line paper claim this script supports>.

Paper anchor: §X.Y (<arc name>).
Inputs:  <prior numbered outputs + cfg.load_*>
Outputs: results/<name>.csv, results/<name>.json
Runtime: <CPU/GPU>, ~<minutes>
\"\"\"

import numpy as np
import pandas as pd

from <module>.api import run

import _config as cfg


def main():
    # 1. Load via cfg
    # 2. Call run() per (dataset, algorithm, ...) — no wrappers
    # 3. Aggregate → DataFrame
    # 4. cfg.save_csv / cfg.save_result
    ...


if __name__ == "__main__":
    main()
```

### Forbidden

- Wrapping `run()` in a helper function.
- Re-implementing primitives the tool already provides.
- `argparse` for anything except `--smoke` (CI flag).
- Path constants inline — use `cfg.*`.
- Cross-script imports. Communicate through files in `results/`.

### Required

- Module docstring naming paper anchor + inputs/outputs/runtime.
- Only project-local import is `import _config as cfg`.
- Output filenames match the script's number prefix.
- A `--smoke` flag that runs in <60s on CPU. CI runs this.

## `_config.py`

Single source of truth for paths, datasets, and I/O. Never duplicate across scripts.

```python
EXPERIMENTS_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR    = EXPERIMENTS_DIR / "analysis"
RESULTS_DIR     = ANALYSIS_DIR / "results"
FIGURES_DIR     = ANALYSIS_DIR / "figures"

DATASETS   = { ... }   # name → {pca: ..., label_key: ...}
ALGORITHMS = [...]
K_SWEEP    = [...]

def load_pca(dataset: str): ...
def load_labels(dataset: str): ...
def save_csv(name: str, df): ...
def save_result(name: str, data): ...
def load_result(name: str): ...
```

When a constant or helper shows up in two scripts, that's the signal it belongs in `_config.py`.

## Running scripts

```bash
# From the tool's venv (so the tool is importable)
cd experiments/tools/<tool>
.venv/bin/python3 ../../analysis/03_<name>.py
.venv/bin/python3 ../../analysis/03_<name>.py --smoke
```

Long jobs go through your cluster submitter, never raw `sbatch --wrap`.

Hydra sweeps (different surface — these launch the tool's CLI, not numbered scripts):

```bash
.venv/bin/python3 -m <module>.main --config-path=../../configs/<tool> \\
  -m experiment=<name> cluster=<profile>
```

## EXPERIMENT_LOG.md

Append-only chronicle. One entry per non-trivial run:

```markdown
## YYYY-MM-DD — NN_<name> <smoke|run>

- **Pin:** <tool> commit `<sha>`, version `x.y.z`
- **Cmd:** `.venv/bin/python3 ../../analysis/NN_<name>.py [...]`
- **Output:** `results/<name>.csv` (N rows)
- **Notes:** <what you actually learned>
```

The point of the log is the human-readable note. Don't auto-generate.

## PROVENANCE.md

Figure → script → CSV mapping. Updated whenever a figure or its inputs change:

```markdown
## Figure N (§X.Y)

- Script: `analysis/NN_figures.py::figure_<name>()`
- Inputs: `results/<name>.csv`
- Producing script: `analysis/NN_<name>.py`
- Generated: YYYY-MM-DD against <tool> `<sha>`
```

## Pre-PR checklist for numbered scripts

- [ ] Module docstring names paper anchor + inputs/outputs/runtime.
- [ ] Only project-local import is `import _config as cfg`.
- [ ] All `run()` calls are direct.
- [ ] `--smoke` flag runs in <60s on CPU.
- [ ] Outputs land in `cfg.RESULTS_DIR` / `cfg.FIGURES_DIR`.
- [ ] `EXPERIMENT_LOG.md` entry added for any shipped data.
- [ ] `PROVENANCE.md` updated if a figure changed.
"""
    claude_path = project_path / "experiments" / "CLAUDE.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] experiments/CLAUDE.md")
    else:
        claude_path.write_text(content)


def create_experiment_log(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Seed experiments/EXPERIMENT_LOG.md with header + format reminder."""
    content = f"""# Experiment Log — {project_name}

Append-only chronicle of non-trivial runs. One entry per run that produced shipped data.

Format:

```markdown
## YYYY-MM-DD — NN_<name> <smoke|run>

- **Pin:** <tool> commit `<sha>`, version `x.y.z`
- **Cmd:** `.venv/bin/python3 ../../analysis/NN_<name>.py [...]`
- **Output:** `results/<name>.csv` (N rows)
- **Notes:** <what you actually learned>
```
"""
    log_path = project_path / "experiments" / "EXPERIMENT_LOG.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] experiments/EXPERIMENT_LOG.md")
    else:
        log_path.write_text(content)


def create_provenance(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Seed experiments/PROVENANCE.md with header + format reminder."""
    content = f"""# Provenance — {project_name}

Figure → script → CSV mapping. Updated whenever a figure or its inputs change.

Format:

```markdown
## Figure N (§X.Y)

- Script: `analysis/NN_figures.py::figure_<name>()`
- Inputs: `results/<name>.csv`
- Producing script: `analysis/NN_<name>.py`
- Generated: YYYY-MM-DD against <tool> `<sha>`
```
"""
    prov_path = project_path / "experiments" / "PROVENANCE.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] experiments/PROVENANCE.md")
    else:
        prov_path.write_text(content)


# Shared agent state (LRW). Templates mirror shop/claude-plugins/lrw-agent-state/templates; keep the two in sync.
LRW_MARKETPLACE = "lrw"
LRW_MARKETPLACE_REPO = "latent-reasoning-works/shop"
LRW_AGENT_STATE_PLUGIN = "lrw-agent-state"


def _git_user_slug() -> str:
    """Lower-case first name from `git config user.name`, for the first log file; 'lead' if unset."""
    try:
        out = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    except OSError:
        out = ""
    import unicodedata
    first = out.split()[0] if out else "lead"
    ascii_first = unicodedata.normalize("NFKD", first).encode("ascii", "ignore").decode()
    return "".join(ch for ch in ascii_first.lower() if ch.isalnum()) or "lead"


def create_agent_state(project_path: Path, project_name: str, dry_run: bool = False) -> None:
    """Seed docs/agent-state/ (board, ledger, decisions, a log), the CLAUDE.md section that imports the board, and
    .claude/settings.json enabling the lrw-agent-state plugin, so collaborators' Claude sessions share state through git."""
    import json

    src = get_template_dir() / "agent-state"
    dst = project_path / "docs" / "agent-state"
    person = _git_user_slug()
    subs = {"{{PROJECT}}": project_name, "{{DATE}}": date.today().isoformat(), "{{LEAD}}": person,
            "{{PERSON}}": person, "{{OWNER_ROWS}}": f"| {person} | (free) | |"}

    def fill(text: str) -> str:
        for k, v in subs.items():
            text = text.replace(k, v)
        return text

    files = {"README.md": "README.md", "board.md": "board.md", "ledger.md": "ledger.md",
             "decisions.md": "decisions.md", "log.md": f"log-{person}.md"}
    settings = {"extraKnownMarketplaces": {LRW_MARKETPLACE: {"source": {"source": "github", "repo": LRW_MARKETPLACE_REPO}}},
                "enabledPlugins": {f"{LRW_AGENT_STATE_PLUGIN}@{LRW_MARKETPLACE}": True}}
    if dry_run:
        for name in files.values():
            console.print(f"  [dim]write[/dim] docs/agent-state/{name}")
        console.print("  [dim]write[/dim] .claude/settings.json")
        console.print("  [dim]append[/dim] CLAUDE.md (shared agent state section)")
        return
    dst.mkdir(parents=True, exist_ok=True)
    for name_in, name_out in files.items():
        (dst / name_out).write_text(fill((src / name_in).read_text()))
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(exist_ok=True)
    (claude_dir / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    claude_md = project_path / "CLAUDE.md"
    snippet = (src / "CLAUDE-snippet.md").read_text()
    if claude_md.exists() and "@docs/agent-state/board.md" not in claude_md.read_text():
        claude_md.write_text(claude_md.read_text().rstrip() + "\n\n" + snippet)


def init_git(project_path: Path, dry_run: bool = False) -> None:
    """Initialize git repository."""
    if dry_run:
        console.print(f"  [dim]git init[/dim]")
        return

    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        capture_output=True,
        check=True,
    )
    # Rename branch to main
    subprocess.run(
        ["git", "branch", "-m", "main"],
        cwd=project_path,
        capture_output=True,
    )


def apply_paper_template(project_path: Path, template: str, dry_run: bool = False) -> None:
    """Apply a paper template to the paper/ directory."""
    template_dir = get_template_dir() / "paper" / template
    paper_dir = project_path / "paper"

    if not template_dir.exists():
        console.print(f"[yellow]Warning:[/yellow] Template '{template}' not found, paper/ will be empty")
        return

    if dry_run:
        console.print(f"  [dim]copy template[/dim] {template} -> paper/")
        return

    # Copy template files to paper/
    for item in template_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, paper_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, paper_dir / item.name)

    console.print(f"  Applied template: {template}")


def link_overleaf_subtree(project_path: Path, overleaf_url: str, dry_run: bool = False) -> None:
    """Link Overleaf project via git subtree."""
    if dry_run:
        console.print(f"  [dim]git remote add overleaf[/dim] {overleaf_url}")
        console.print(f"  [dim]git subtree add --prefix=paper overleaf master --squash[/dim]")
        return

    # Remove placeholder paper directory
    paper_dir = project_path / "paper"
    if paper_dir.exists():
        shutil.rmtree(paper_dir)

    # Add remote
    subprocess.run(
        ["git", "remote", "add", "overleaf", overleaf_url],
        cwd=project_path,
        capture_output=True,
        check=True,
    )

    # Fetch and add subtree
    console.print("[cyan]Fetching from Overleaf (credentials may be required)...[/cyan]")
    subprocess.run(
        ["git", "fetch", "overleaf"],
        cwd=project_path,
        check=True,
    )

    subprocess.run(
        ["git", "subtree", "add", "--prefix=paper", "overleaf", "master", "--squash"],
        cwd=project_path,
        check=True,
    )


def show_project_tree(project_path: Path, project_name: str) -> None:
    """Display project structure as a tree."""
    tree = Tree(f"[bold green]{project_name}/[/bold green]")

    def add_to_tree(parent: Tree, path: Path, depth: int = 0) -> None:
        if depth > 2:
            return
        try:
            entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for entry in entries:
                if entry.name.startswith(".") and entry.name != ".gitignore":
                    continue
                if entry.is_dir():
                    branch = parent.add(f"[blue]{entry.name}/[/blue]")
                    add_to_tree(branch, entry, depth + 1)
                else:
                    parent.add(f"[dim]{entry.name}[/dim]")
        except PermissionError:
            pass

    add_to_tree(tree, project_path)
    console.print(tree)


def create_project(
    name: str,
    parent_path: str = ".",
    tools: list[str] = None,
    overleaf_url: str = None,
    template: str = "blank",
    dry_run: bool = False,
) -> Path:
    """Create a new research project.

    Args:
        name: Project name (will be directory name)
        parent_path: Parent directory to create project in
        tools: List of tools to add (registry names or URLs)
        overleaf_url: Overleaf Git URL to link
        template: Paper template to use
        dry_run: If True, show what would be created without creating

    Returns:
        Path to created project
    """
    tools = tools or []
    project_path = Path(parent_path).resolve() / name

    if dry_run:
        console.print(f"\n[bold]Dry run:[/bold] Would create project at {project_path}\n")
    else:
        if project_path.exists():
            console.print(f"[red]Error:[/red] Directory {project_path} already exists")
            raise SystemExit(1)
        console.print(f"\n[bold green]Creating project:[/bold green] {name}\n")

    # Create directory structure
    if not dry_run:
        project_path.mkdir(parents=True)
    create_directory_structure(project_path, PROJECT_STRUCTURE, dry_run)

    # Copy experimentStash scripts
    copy_experimentstash_scripts(project_path, dry_run)

    # Create config files
    create_meta_yaml(project_path, name, dry_run)
    create_gitignore(project_path, dry_run)
    create_readme(project_path, name, dry_run)
    create_claude_md(project_path, name, dry_run)
    create_experiments_claude_md(project_path, dry_run)
    create_experiment_log(project_path, name, dry_run)
    create_provenance(project_path, name, dry_run)
    create_agent_state(project_path, name, dry_run)

    # Initialize git
    init_git(project_path, dry_run)

    # Initial commit before adding subtree
    if not dry_run:
        subprocess.run(
            ["git", "add", "."],
            cwd=project_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial project structure"],
            cwd=project_path,
            capture_output=True,
        )

    # Link Overleaf if provided, otherwise apply template
    if overleaf_url:
        console.print(f"\n[cyan]Linking Overleaf project...[/cyan]")
        link_overleaf_subtree(project_path, overleaf_url, dry_run)
    elif template:
        # Apply paper template
        apply_paper_template(project_path, template, dry_run)

    # Add tools
    if tools:
        console.print(f"\n[cyan]Adding tools...[/cyan]")
        from expaper.tools import add_tool_to_project
        for tool in tools:
            if not dry_run:
                # Change to project directory for tool addition
                old_cwd = os.getcwd()
                os.chdir(project_path)
                try:
                    add_tool_to_project(tool)
                finally:
                    os.chdir(old_cwd)
            else:
                console.print(f"  [dim]add tool[/dim] {tool}")

    # Show result
    if not dry_run:
        console.print(f"\n[bold green]Project created successfully![/bold green]\n")
        show_project_tree(project_path, name)
        console.print(f"\n[dim]cd {project_path}[/dim]")

        if not overleaf_url:
            console.print(
                "\n[yellow]Tip:[/yellow] Link Overleaf later with:\n"
                f"  expaper link-overleaf https://git.overleaf.com/YOUR_PROJECT_ID"
            )

    return project_path
