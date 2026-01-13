# expaper

Research project scaffolding tool combining **experimentStash** structure with **Overleaf** integration.

## Standalone vs Monorepo

expaper supports two modes:

### Standalone Mode
The expaper IS the git repository:
```
my-paper/                             # Git root = expaper root
├── paper/                            # Subtree prefix: "paper"
├── experiments/
├── shared/
└── CLAUDE.md
```

### Monorepo Mode
The expaper is a subdirectory within a larger repo:
```
research-monorepo/                    # Git root
├── CLAUDE.md                         # Monorepo orchestration
├── first-paper/                      # expaper #1
│   ├── paper/                        # Subtree prefix: "first-paper/paper"
│   ├── experiments/
│   ├── shared/
│   └── CLAUDE.md
├── second-paper/                     # expaper #2
│   └── ...
└── pyproject.toml                    # (optional) shared deps
```

### Key Difference: Subtree Prefix

| Mode | Subtree prefix | Sync command |
|------|----------------|--------------|
| Standalone | `paper` | `git subtree pull --prefix=paper ...` |
| Monorepo | `{expaper}/paper` | `git subtree pull --prefix=first-paper/paper ...` |

expaper detects which mode by checking if cwd is the git root:
- **At git root** → standalone (or run `expaper init` to create monorepo child)
- **In subdirectory** → monorepo mode, prefix includes path from git root

### Monorepo Benefits
- Multiple papers sharing one git repo
- Cross-referencing experiments between papers
- Single source of truth for shared tools/configs

## Quick Reference

```bash
# Development setup
cd ~/expaper
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run CLI (from monorepo root)
expaper --help
expaper init my-paper --template blank    # Creates my-paper/ subdirectory
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
Creates an expaper subdirectory within a monorepo:
```
monorepo/
└── my-paper/                       # expaper subdirectory
    ├── experiments/
    │   ├── configs/meta.yaml       # Tool registry for this expaper
    │   ├── tools/                  # Git submodules
    │   ├── scripts/                # add_tool, run_experiment, snapshot_experiment
    │   ├── notebooks/
    │   └── outputs/
    ├── paper/                      # Overleaf-synced (git subtree)
    ├── shared/bib/, figures/, sty/
    └── CLAUDE.md
```

Key functions:
- `create_project()` - Main entry point
- `link_overleaf_subtree()` - Sets up git subtree
- `apply_paper_template()` - Copies template to paper/
- `copy_experimentstash_scripts()` - Bundles scripts into project

### `overleaf.py` - Overleaf Integration
Uses **git subtree** (NOT submodule) for bidirectional sync.

**Prefix depends on mode** (see "Standalone vs Monorepo" above):
```bash
# Standalone (expaper is git root):
git subtree pull --prefix=paper overleaf master --squash

# Monorepo (expaper is subdirectory):
git subtree pull --prefix=my-paper/paper overleaf master --squash
```

Key functions:
- `get_subtree_prefix()` - Computes correct prefix based on git root location
- `sync_pull()` - `git subtree pull --prefix={prefix} overleaf master --squash`
- `sync_push()` - `git subtree push --prefix={prefix} overleaf master`
- `link_overleaf()` - Adds remote and creates subtree with correct prefix

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
# Create expaper
expaper init my-paper                             # Creates my-paper/ (monorepo) or initializes cwd (standalone)
expaper init my-paper --overleaf URL              # Link Overleaf during init
expaper init my-paper --tools geomancy            # Add tool during init
expaper init my-paper --dry-run                   # Preview only

# Manage tools (run from expaper directory)
expaper tool list                                 # Project tools
expaper tool list --registry                      # Available tools
expaper tool add geomancy                         # From registry
expaper tool add mytool https://github.com/x/y   # From URL

# Overleaf sync (run from expaper directory, auto-detects prefix)
expaper sync pull                                 # Get changes
expaper sync push                                 # Push changes
expaper sync status                               # Show status
expaper link-overleaf URL                         # Link existing Overleaf project

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

## LRW Infrastructure Detection

When expaper detects LRW-specific infrastructure (e.g., shop integration, specific tool patterns), it should generate **delegated CLAUDE.md files** in subdirectories rather than a single root-level file.

### Detection Signals
Look for these patterns indicating LRW infrastructure:
- `shop/` directory or shop-related configs
- Tools from LRW registry (manylatents, geomancy, etc.)
- Hydra configs with LRW-specific patterns
- `.shop.yaml` or similar config files

### Delegated CLAUDE.md Structure

When LRW infrastructure is detected, generate:

```
project/
├── CLAUDE.md                    # Root: project overview + delegation
├── experiments/
│   └── CLAUDE.md                # Agentic context for running experiments
└── paper/
    └── CLAUDE.md                # Agentic context for paper writing
```

### Root CLAUDE.md (with LRW)

The root CLAUDE.md serves as **orchestrator**, delegating to subdirectory contexts:

```markdown
# {project_name}

Research project combining experiments and paper writing.

## Delegation

**This project has specialized context files:**

- **Experiments**: See `experiments/CLAUDE.md` for running experiments, tool configs, Hydra workflows
- **Paper**: See `paper/CLAUDE.md` for paper writing, Overleaf sync, narrative directives

When working in a subdirectory, read its CLAUDE.md first.

## Cross-Cutting Concerns

### Shared Resources
- `shared/figures/` - Figures used in paper (generated from experiments)
- `shared/bib/` - Bibliography files

### Figure Workflow
1. Run experiment → outputs to `experiments/outputs/`
2. Generate figure → save to `shared/figures/`
3. Include in paper → `\includegraphics{../shared/figures/...}`

### Sync Status
- Overleaf: `expaper sync status`
- Tools: Check `experiments/configs/meta.yaml`
```

### experiments/CLAUDE.md
Agentic context for experiment workflows:
- Tool-specific commands and entrypoints
- Hydra config structure and overrides
- How to run experiments (`run_experiment`)
- How to snapshot for reproducibility (`snapshot_experiment`)
- Output directory conventions
- Shop integration specifics (if present)

### paper/CLAUDE.md
Agentic context for paper writing:
- LaTeX structure and main entry point
- Figure inclusion conventions (paths to shared/figures)
- Bibliography management (shared/bib)
- Conference-specific formatting notes

**Overleaf-specific guidance:**
- Sync workflow: `expaper sync pull` before editing, `expaper sync push` after
- Credential handling (git credential helper)
- Conflict resolution when collaborators edit simultaneously
- What NOT to do: don't edit directly on Overleaf while local changes are uncommitted
- Commit message conventions for paper changes

### paper/CLAUDE.md Template

Each Overleaf-linked paper gets its own CLAUDE.md with:
1. **Overleaf sync workflow** (generic)
2. **Experiment context** (project-specific)
3. **Narrative directives** (project-specific)

```markdown
# Paper: {project_name}

## Overleaf Sync

This paper is synced with Overleaf via git subtree.

### Workflow
1. Pull before editing: `cd .. && expaper sync pull`
2. Edit paper files
3. Commit and push: `git add paper/ && git commit -m "msg" && cd .. && expaper sync push`

### Credentials
- Username: Overleaf email
- Password: Overleaf password or Git token

---

## Experiment Context

This paper documents experiments from `../experiments/`.

### Key Experiments
<!-- Populated based on experiments/configs/ -->
- **{experiment_1}**: {brief description}
- **{experiment_2}**: {brief description}

### Results Location
- Outputs: `../experiments/outputs/`
- Figures: `../shared/figures/`

### Reproducibility
To regenerate results:
```bash
cd ../experiments
python scripts/run_experiment {tool} {config}
```

---

## Narrative Directives

### Paper Thesis
<!-- User should fill this in -->
{What is this paper arguing/demonstrating?}

### Key Claims
1. {Claim 1 - supported by which experiment?}
2. {Claim 2 - supported by which experiment?}

### Story Arc
- **Problem**: {What problem does this solve?}
- **Approach**: {What's the method/contribution?}
- **Evidence**: {Which experiments support this?}
- **Impact**: {Why does this matter?}

### Writing Guidelines
- Keep methods reproducible (reference configs)
- Figures should be generated from experiment outputs
- Claims must map to specific experimental results
```

### Why Per-Paper CLAUDE.md?

Each paper has unique:
- **Experiments it covers**: Different subset of tools/configs
- **Narrative**: What story is being told
- **Claims**: What's being argued, backed by which data
- **Audience**: Conference-specific framing (ICML vs NeurIPS vs workshop)

This context helps Claude:
- Write sections that connect to actual experiment results
- Maintain narrative consistency across edits
- Know which figures/tables to reference
- Avoid making claims not supported by experiments

### Implementation Location
This logic should be added to `scaffold.py:create_claude_md()`:
1. Check for LRW infrastructure signals
2. If detected: generate three CLAUDE.md files with delegation
3. If not detected: generate single root CLAUDE.md (current behavior)

### Why Delegation?
- **Context efficiency**: Claude works in one directory at a time; relevant context should be local
- **Workflow separation**: Experiment running vs paper writing are distinct agentic tasks
- **Tool awareness**: experiments/CLAUDE.md can reference specific tool docs/patterns
- **Reduced noise**: Paper context doesn't need experiment details and vice versa

## Future Enhancements

Potential improvements:
- `--dry-run` flag for sync commands
- Better detection of remote changes in `sync status`
- Support for non-master Overleaf branches
- Hooks for pre/post sync operations
- Figure sync between experiments/outputs and paper/figures
- **LRW infrastructure auto-detection and delegated CLAUDE.md generation**
