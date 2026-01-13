# expaper

Research project scaffolding tool combining **experimentStash** structure with **Overleaf** integration.

## Quick Reference

```bash
# Development setup
cd ~/expaper
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run CLI
expaper --help
expaper init my-project --template blank
expaper tool add hydra-test-tool
expaper sync pull
```

## Architecture

```
expaper/
├── expaper/                    # Main package
│   ├── __init__.py             # Version
│   ├── cli.py                  # Click-based CLI entrypoint
│   ├── scaffold.py             # Project scaffolding logic
│   ├── overleaf.py             # Git subtree sync operations
│   ├── tools.py                # Tool registry + management
│   └── templates/
│       ├── __init__.py         # Template functions (list, create, export)
│       ├── registry.yaml       # Bundled tool registry
│       ├── gitignore           # LaTeX + Python gitignore
│       ├── scripts/            # experimentStash scripts (add_tool, run_experiment, snapshot_experiment)
│       └── paper/
│           ├── blank/          # Minimal LaTeX template
│           └── arxiv/          # arxiv template (placeholder)
├── tests/
├── pyproject.toml              # Package config, CLI entrypoint
└── README.md
```

## Key Modules

### `cli.py` - Command Line Interface
Click-based CLI with these command groups:
- `expaper init <name>` - Create new project
- `expaper tool add|list` - Manage experiment tools
- `expaper sync pull|push|status` - Overleaf sync
- `expaper template list|create|export` - Paper templates
- `expaper link-overleaf <url>` - Link existing Overleaf project

### `scaffold.py` - Project Creation
Creates directory structure:
```
project/
├── experiments/
│   ├── configs/meta.yaml       # Tool registry for this project
│   ├── tools/                  # Git submodules
│   ├── scripts/                # add_tool, run_experiment, snapshot_experiment
│   ├── notebooks/
│   └── outputs/
├── paper/                      # Overleaf-synced (git subtree)
├── shared/bib/, figures/
├── .gitignore
├── CLAUDE.md
└── README.md
```

Key functions:
- `create_project()` - Main entry point
- `link_overleaf_subtree()` - Sets up git subtree
- `apply_paper_template()` - Copies template to paper/
- `copy_experimentstash_scripts()` - Bundles scripts into project

### `overleaf.py` - Overleaf Integration
Uses **git subtree** (NOT submodule) for bidirectional sync.

Key functions:
- `sync_pull()` - `git subtree pull --prefix=paper overleaf master --squash`
- `sync_push()` - `git subtree push --prefix=paper overleaf master`
- `link_overleaf()` - Adds remote and creates subtree

### `tools.py` - Tool Registry
Manages experiment tools via registry lookup or direct URL.

Registry locations:
1. Bundled: `expaper/templates/registry.yaml`
2. User: `~/.config/expaper/registry.yaml` (overrides bundled)

Key functions:
- `load_registry()` - Merges bundled + user registries
- `add_tool_to_project()` - Wraps experimentStash's add_tool script

### `templates/__init__.py` - Template Management
- `list_templates()` - Shows available templates
- `create_from_template()` - Creates paper/ from template
- `export_paper_zip()` - Packages paper/ for Overleaf upload

## Critical Pitfalls

### 1. Overleaf Has NO Public API for Creating Projects
**This is a fundamental limitation.** expaper CANNOT:
- Create Overleaf projects programmatically
- Push content to a new Overleaf project directly

**Workaround workflow:**
1. User creates Overleaf project manually (from gallery or blank)
2. User gets Git URL: Menu -> Git -> Copy URL
3. Link with: `expaper link-overleaf https://git.overleaf.com/PROJECT_ID`

Conference templates (ICML, NeurIPS, ICLR) should be created from Overleaf's gallery, not bundled.

### 2. Git Subtree vs Submodule
expaper uses **git subtree** for Overleaf, which:
- Stores content directly in repo (no `.gitmodules`)
- Allows bidirectional sync without submodule complexity
- Creates merge commits for pull operations

Common issues:
- "prefix already exists" - Delete paper/ directory before linking
- "working tree has modifications" - Commit changes before subtree operations

### 3. Overleaf Authentication
Overleaf Git requires credentials:
- Username: Overleaf email
- Password: Overleaf password OR Git token (Account Settings)

Cache credentials:
```bash
git config --global credential.helper cache   # 15 min
git config --global credential.helper store   # permanent
```

### 4. Project Root Detection
Many commands need to find the project root. They look for:
- `experiments/configs/meta.yaml` (tools.py)
- `experiments/` or `paper/` directory (overleaf.py)

Running commands from wrong directory = errors.

### 5. Template Must Be Applied AFTER Directory Creation
In `create_project()`, the order matters:
1. Create directory structure (creates empty `paper/`)
2. If Overleaf URL provided: delete `paper/`, then `subtree add`
3. If no Overleaf URL: apply template to `paper/`

## CLI Commands Reference

```bash
# Create project
expaper init my-project                           # Blank template
expaper init my-project --overleaf URL            # Link Overleaf
expaper init my-project --tools geomancy          # Add tool
expaper init my-project --dry-run                 # Preview only

# Manage tools
expaper tool list                                 # Project tools
expaper tool list --registry                      # Available tools
expaper tool add geomancy                         # From registry
expaper tool add mytool https://github.com/x/y   # From URL

# Overleaf sync
expaper sync pull                                 # Get changes
expaper sync push                                 # Push changes
expaper sync status                               # Show status
expaper link-overleaf URL                         # Link existing

# Templates
expaper template list                             # Available templates
expaper template create blank                     # Apply template
expaper template export                           # Export ZIP
```

## Development Workflow

### Setup
```bash
cd ~/expaper
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Testing
```bash
pytest                          # Run all tests
pytest -v                       # Verbose
pytest tests/test_scaffold.py   # Specific file
```

### Test a full workflow
```bash
cd /tmp
expaper init test-project --template blank
cd test-project
expaper tool list
expaper sync status
```

### Adding a new template
1. Create directory in `expaper/templates/paper/<name>/`
2. Add main.tex and supporting files
3. Update descriptions dict in `templates/__init__.py:list_templates()`

### Adding a tool to registry
Edit `expaper/templates/registry.yaml`:
```yaml
tools:
  mytool:
    url: https://github.com/user/mytool
    entrypoint: "-m mytool.main"
    description: "My tool description"
```

## Dependencies

```toml
dependencies = [
    "click>=8.0",           # CLI framework
    "pyyaml>=6.0",          # Config parsing
    "rich>=13.0",           # Pretty terminal output
    "jinja2>=3.0",          # Template rendering
]
```

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Not in an expaper project directory" | Wrong cwd or missing meta.yaml | cd to project root |
| "prefix 'paper' already exists" | paper/ not empty before subtree | rm -rf paper/ first |
| "working tree has modifications" | Uncommitted changes | git commit first |
| "No Overleaf remote configured" | Missing remote | expaper link-overleaf URL |
| "Tool not found in registry" | Not in registry | Provide URL or add to registry |

## Generated Project CLAUDE.md

When expaper creates a project, it generates a CLAUDE.md with:
- Project structure explanation
- Key commands for experiments and sync
- Workflow guidance for paper editing

See `scaffold.py:create_claude_md()` for template.

## Future Enhancements

Potential improvements:
- `--dry-run` flag for sync commands
- Better detection of remote changes in `sync status`
- Support for non-master Overleaf branches
- Hooks for pre/post sync operations
- Figure sync between experiments/outputs and paper/figures
