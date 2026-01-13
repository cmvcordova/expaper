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
  --template       Paper template (default: blank)
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

## Overleaf Integration

### Limitation

Overleaf has **no public API for creating projects**. This means:
- expaper cannot create Overleaf projects programmatically
- You must create the Overleaf project manually first
- expaper then links to it via Git for bidirectional sync

### Recommended Workflow

**Option A: Start from Overleaf (recommended for conference papers)**

1. Go to [Overleaf Gallery](https://www.overleaf.com/gallery) and create a project from a conference template (ICML, NeurIPS, ICLR, etc.)
2. Get the Git URL: Menu → Git → Copy URL
3. Create your expaper project:
   ```bash
   expaper init my-research --overleaf https://git.overleaf.com/YOUR_PROJECT_ID
   ```

**Option B: Start locally, link later**

1. Create project with blank template:
   ```bash
   expaper init my-research --template blank
   ```
2. Later, create Overleaf project and link:
   ```bash
   cd my-research
   expaper link-overleaf https://git.overleaf.com/YOUR_PROJECT_ID
   ```

### Sync Commands

```bash
# Pull collaborator changes from Overleaf
expaper sync pull

# Push your local changes to Overleaf
expaper sync push

# Check sync status
expaper sync status
```

### Credentials

Overleaf Git requires authentication:
- **Username**: Your Overleaf email
- **Password**: Your Overleaf password (or Git token from Account Settings)

To cache credentials:
```bash
git config --global credential.helper cache   # Temporary (15 min)
git config --global credential.helper store   # Permanent (less secure)
```

## Complete Workflow

1. **Create Overleaf project** from conference template
2. **Init expaper project**: `expaper init my-research --overleaf URL`
3. **Add experiment tools**: `expaper tool add geomancy`
4. **Run experiments**: `python experiments/scripts/run_experiment tool config`
5. **Edit paper**: Work in `paper/` directory
6. **Sync with collaborators**:
   ```bash
   expaper sync pull   # Get their changes
   git add paper/ && git commit -m "Update results"
   expaper sync push   # Push your changes
   ```
7. **Snapshot for reproducibility**:
   ```bash
   python experiments/scripts/snapshot_experiment tool exp --tag camera-ready --commit
   ```

## License

MIT
