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
└── CLAUDE.md             # AI assistant context
```

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
    """Create CLAUDE.md for AI assistant context."""
    content = f"""# {project_name}

Research project combining experiments and paper writing.

## Structure

```
experiments/
  configs/<tool>/          # Hydra config stash (experiment overrides only)
    experiment/            # Sweep configs (project-specific)
    config.yaml            # Base defaults list (copied from tool)
  tools/<tool>/            # Git submodules
  scripts/                 # add_tool, run_experiment, snapshot_experiment
  outputs/                 # Experiment results (gitignored)
paper/                     # LaTeX paper synced with Overleaf
shared/bib/, figures/      # Shared resources
```

## Running experiments

Direct invocation from the tool directory (not via bridge scripts):

```bash
cd experiments/tools/<tool>
python3 -m <module>.main --config-path=../../configs/<tool> \\
  experiment=<name> <extra overrides>
```

Use `experiment=<name>` (Hydra group override), not `--config-name`.

## Config resolution

Three layers, highest priority first:
1. **CLI overrides** — `data.n_samples=500`
2. **Config stash** (`--config-path`) — `experiments/configs/<tool>/`
3. **Package defaults** (`pkg://`) — inside the tool itself

The stash only contains `config.yaml` and `experiment/` overrides.
Tool configs (algorithms/, data/, metrics/) resolve from pkg:// at runtime.
Don't copy them into the stash — stale copies silently shadow upstream defaults.

## Extension discovery

Tools register extensions via `pyproject.toml` entry points. The tool discovers
them with `importlib.metadata.entry_points()` — no hardcoded imports needed.

## Overleaf sync

```bash
expaper sync pull   # Get collaborator changes
expaper sync push   # Push local changes
```

## Working with this project

- Use `uv` for dependency management, never `pip install`
- Use `python3` (not `python`) on cluster environments
- Snapshot experiments before paper submission: `python3 scripts/snapshot_experiment`
"""
    claude_path = project_path / "CLAUDE.md"
    if dry_run:
        console.print(f"  [dim]write[/dim] CLAUDE.md")
    else:
        claude_path.write_text(content)


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
