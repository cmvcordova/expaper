<div align="center">

<pre>
    paper/          experiments/
   ┌────────┐      ┌──────────────┐
   │ main.tex│ ←── │ tools/       │
   │ bib/    │     │ configs/     │
   │ figs/   │     │ outputs/     │
   └────────┘      └──────────────┘
        ↕                ↕
     overleaf       experimentStash

         e x p a p e r

  reproducible research, from scaffold to camera-ready
</pre>

[![license](https://img.shields.io/badge/license-MIT-2DD4BF.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.11+-2DD4BF.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/pkg-uv-2DD4BF.svg)](https://docs.astral.sh/uv/)

</div>

---

## quickstart

```bash
uv pip install -e .

# interactive setup — prompts for tools and Overleaf
expaper init my-research

# or fully specified
expaper init my-research \
  --tools manylatents \
  --overleaf https://git.overleaf.com/abc123
```

---

## architecture

```
my-research/
├── experiments/           # experimentStash
│   ├── configs/           # Hydra configs (copied from tools, read-only)
│   │   └── meta.yaml      # tool registry
│   ├── tools/             # git submodules (pinned tools)
│   ├── scripts/           # add_tool, snapshot_experiment
│   └── outputs/           # experiment results
├── paper/                 # Overleaf-synced (git subtree)
├── shared/
│   ├── bib/               # bibliography
│   └── figures/           # shared figures
├── CLAUDE.md              # AI assistant context (delegates to tool CLAUDE.mds)
└── README.md
```

Three layers for config composition (highest to lowest precedence):

| Layer | Where | When |
|-------|-------|------|
| CLI overrides | command line | always available |
| Experiment configs | `configs/<tool>/experiment/` | sweep definitions |
| Base configs (read-only) | `configs/<tool>/` | copied from tool, never edited |

---

## commands

```bash
# create project (interactive wizard)
expaper init <name>
expaper init <name> --no-interactive   # skip prompts

# add tools
expaper tool add <name>              # from registry
expaper tool add <name> <url>        # from URL
expaper tool list --registry         # show available tools

# local build (free, no Overleaf needed)
expaper build                        # compile paper/main.tex → main.pdf
expaper build --clean                # remove artifacts first
expaper build --open                 # compile + open PDF

# overleaf sync (alternative to local build)
expaper sync pull                    # pull collaborator changes
expaper sync push                    # push local changes
expaper sync status                  # check sync state
expaper link-overleaf <url>          # link after project creation
```

---

## workflow

```
1. expaper init my-paper --overleaf URL
2. expaper tool add manylatents
3. cd experiments/tools/manylatents
   uv run python -m manylatents.main --multirun ...
4. edit paper/main.tex with results
5. expaper sync push
6. python3 experiments/scripts/snapshot_experiment manylatents exp --tag v1
```

---

## overleaf

Overleaf has no API for creating projects. Create the project on Overleaf first, then link:

1. Create project on [Overleaf](https://www.overleaf.com) (or from a conference template)
2. Copy Git URL: Menu > Git > Copy URL
3. `expaper init my-paper --overleaf https://git.overleaf.com/<id>`

Or link later: `expaper link-overleaf https://git.overleaf.com/<id>`

Credentials: use `git config --global credential.helper store` to avoid re-entering.

---

## tool registry

Bundled tools in `expaper/templates/registry.yaml`. Extend with:

```yaml
# ~/.config/expaper/registry.yaml
tools:
  mytool:
    url: https://github.com/user/mytool
    entrypoint: "-m mytool.main"
    description: "My custom tool"
```

---

<br>

<p align="center">
<sub>MIT License &middot; <a href="https://github.com/cmvcordova">cmvcordova</a></sub>
</p>
