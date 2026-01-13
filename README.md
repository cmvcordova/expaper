# expaper

Research project scaffolding tool combining **experimentStash** structure with **Overleaf** integration.

## Installation

```bash
# With uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

```bash
# Create a new research project
expaper init my-research

# Create with Overleaf integration
expaper init my-research --overleaf https://git.overleaf.com/YOUR_PROJECT_ID

# Add experiment tools
expaper tool add geomancy
expaper tool add mytool https://github.com/user/repo

# Sync with Overleaf
expaper sync pull   # Get collaborator changes
expaper sync push   # Push your changes
```

## Generated Project Structure

```
my-research/
├── experiments/           # experimentStash structure
│   ├── configs/           # Hydra configurations
│   │   └── meta.yaml      # Tool registry
│   ├── tools/             # Git submodules
│   ├── scripts/           # add_tool, run_experiment, snapshot_experiment
│   ├── notebooks/         # Analysis notebooks
│   └── outputs/           # Experiment results
├── paper/                 # Overleaf-synced paper
│   └── main.tex
├── shared/                # Shared resources
│   ├── bib/               # Bibliography
│   └── figures/           # Figures for paper
├── .gitignore
├── CLAUDE.md              # AI assistant context
└── README.md
```

## Commands

### `expaper init`

Create a new research project:

```bash
expaper init <name> [options]

Options:
  --path, -p       Parent directory (default: current)
  --tools, -t      Tools to add (repeatable)
  --overleaf, -o   Overleaf Git URL to link
  --template       Paper template (blank, icml2026, neurips2025, arxiv)
  --dry-run        Show what would be created
```

### `expaper tool`

Manage experiment tools:

```bash
expaper tool add <name> [url]     # Add from registry or URL
expaper tool list                  # List project tools
expaper tool list --registry       # List available tools
```

### `expaper sync`

Sync with Overleaf:

```bash
expaper sync pull      # Pull from Overleaf
expaper sync push      # Push to Overleaf
expaper sync status    # Show sync status
```

### `expaper template`

Manage paper templates:

```bash
expaper template list              # List templates
expaper template create <name>     # Create paper from template
expaper template export            # Export paper as ZIP
```

### `expaper link-overleaf`

Link an existing Overleaf project:

```bash
expaper link-overleaf https://git.overleaf.com/YOUR_PROJECT_ID
```

## Tool Registry

expaper includes a bundled registry of common tools. Extend it by creating:

```yaml
# ~/.config/expaper/registry.yaml
tools:
  mytool:
    url: https://github.com/user/mytool
    entrypoint: "-m mytool.main"
    description: "My custom tool"
```

## Workflow

1. **Create project**: `expaper init my-research --overleaf URL`
2. **Add tools**: `expaper tool add geomancy`
3. **Run experiments**: `python experiments/scripts/run_experiment tool config`
4. **Edit paper**: Work in `paper/` directory
5. **Sync changes**: `expaper sync push` / `expaper sync pull`
6. **Snapshot for reproducibility**: `python experiments/scripts/snapshot_experiment tool exp --tag v1.0`

## License

MIT
