# expaper

Research project scaffolding — experimentStash + Overleaf/tectonic in one repo.

## Entry Points

```bash
# Create project (interactive wizard)
expaper init my-research

# Non-interactive
expaper init my-research --tools manylatents --overleaf https://git.overleaf.com/abc123 --no-interactive

# Development setup
uv pip install -e .
```

## Architecture

```
expaper/
├── expaper/
│   ├── cli.py              # Click CLI (init, tool, sync, build, link-overleaf)
│   ├── scaffold.py         # Project creation (create_project, create_claude_md)
│   ├── build.py            # Local LaTeX compilation (tectonic)
│   ├── overleaf.py         # Git subtree sync (pull, push, status, link)
│   ├── tools.py            # Tool registry + add_tool_to_project
│   └── templates/
│       ├── registry.yaml   # Bundled tool registry
│       ├── scripts/        # experimentStash scripts (add_tool, snapshot_experiment)
│       └── paper/          # LaTeX templates (blank)
└── pyproject.toml          # CLI entrypoint: expaper = expaper.cli:main
```

## Key Design Decisions

- **paper/ is the canonical source** — same directory for both Overleaf and local builds.
- **Overleaf = git subtree** (not submodule) — bidirectional sync, content stored in repo.
- **Local build = tectonic** — `expaper build` compiles paper/main.tex. Free, no Overleaf needed.
- **Tools = git submodule** — pinned commits, isolated deps via `uv sync`.
- **CLAUDE.md delegation** — root points to subdirectory contexts, never duplicates.
- **Interactive by default** — prompts for tools + Overleaf on init, skip with `--no-interactive`.
- **Config copies are read-only** — customization via CLI overrides or experiment YAML only.

## Commands

```bash
expaper init <name> [--tools T] [--overleaf URL] [--no-interactive] [--dry-run]
expaper build [--clean] [--open]
expaper tool add <name> [url]
expaper tool list [--registry]
expaper sync pull | push | status
expaper link-overleaf <url>
```

## Testing

```bash
uv run pytest
expaper init /tmp/test-project --dry-run --no-interactive
```
