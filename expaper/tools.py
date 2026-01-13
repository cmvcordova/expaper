"""Tool registry and management."""

import subprocess
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.table import Table

console = Console()


def get_registry_path() -> Path:
    """Get path to bundled tool registry."""
    return Path(__file__).parent / "templates" / "registry.yaml"


def get_user_registry_path() -> Path:
    """Get path to user's custom registry."""
    return Path.home() / ".config" / "expaper" / "registry.yaml"


def load_registry() -> dict:
    """Load tool registry (bundled + user extensions)."""
    registry = {"tools": {}}

    # Load bundled registry
    bundled_path = get_registry_path()
    if bundled_path.exists():
        with open(bundled_path) as f:
            bundled = yaml.safe_load(f) or {}
            registry["tools"].update(bundled.get("tools", {}))

    # Load user registry (overrides bundled)
    user_path = get_user_registry_path()
    if user_path.exists():
        with open(user_path) as f:
            user = yaml.safe_load(f) or {}
            registry["tools"].update(user.get("tools", {}))

    return registry


def get_tool_info(name: str) -> Optional[dict]:
    """Get tool info from registry by name."""
    registry = load_registry()
    return registry["tools"].get(name)


def is_url(s: str) -> bool:
    """Check if string looks like a Git URL."""
    return s.startswith(("http://", "https://", "git@", "git://"))


def find_project_root() -> Optional[Path]:
    """Find the project root (directory with experiments/configs/meta.yaml)."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        meta_path = parent / "experiments" / "configs" / "meta.yaml"
        if meta_path.exists():
            return parent
    return None


def add_tool_to_project(
    name: str,
    url: Optional[str] = None,
    entrypoint: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    """Add a tool to the current project.

    Args:
        name: Tool name (registry name or custom name if URL provided)
        url: Git URL (optional if name is in registry)
        entrypoint: Tool entrypoint (optional, auto-detected or from registry)
        description: Tool description (optional)
    """
    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        console.print("[dim]Run this command from within a project created by 'expaper init'[/dim]")
        raise SystemExit(1)

    # Resolve tool info
    if url is None:
        # Look up in registry
        tool_info = get_tool_info(name)
        if tool_info is None:
            console.print(f"[red]Error:[/red] Tool '{name}' not found in registry")
            console.print("[dim]Provide a URL or add to ~/.config/expaper/registry.yaml[/dim]")
            raise SystemExit(1)
        url = tool_info["url"]
        entrypoint = entrypoint or tool_info.get("entrypoint", f"-m {name}.main")
        description = description or tool_info.get("description", f"{name} tool")
    else:
        # Custom tool with URL
        entrypoint = entrypoint or f"-m {name}.main"
        description = description or f"{name} tool"

    console.print(f"[cyan]Adding tool:[/cyan] {name}")
    console.print(f"  URL: {url}")
    console.print(f"  Entrypoint: {entrypoint}")

    # Check if add_tool script exists
    add_tool_script = project_root / "experiments" / "scripts" / "add_tool"
    if not add_tool_script.exists():
        console.print("[red]Error:[/red] experiments/scripts/add_tool not found")
        raise SystemExit(1)

    # Run add_tool script
    cmd = [
        "python",
        str(add_tool_script),
        name,
        url,
        "--entrypoint",
        entrypoint,
        "--description",
        description,
    ]

    result = subprocess.run(
        cmd,
        cwd=project_root / "experiments",
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print(f"[red]Error adding tool:[/red]")
        console.print(result.stderr or result.stdout)
        raise SystemExit(1)

    console.print(f"[green]Tool '{name}' added successfully[/green]")


def list_registry_tools(show_registry: bool = False) -> None:
    """List tools in current project or registry.

    Args:
        show_registry: If True, show available tools in registry.
                      If False, show tools in current project.
    """
    if show_registry:
        registry = load_registry()
        tools = registry.get("tools", {})

        if not tools:
            console.print("[yellow]No tools in registry[/yellow]")
            return

        table = Table(title="Available Tools in Registry")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="dim")
        table.add_column("Description")

        for name, info in sorted(tools.items()):
            table.add_row(
                name,
                info.get("url", ""),
                info.get("description", ""),
            )

        console.print(table)
    else:
        # Show tools in current project
        project_root = find_project_root()
        if not project_root:
            console.print("[red]Error:[/red] Not in an expaper project directory")
            raise SystemExit(1)

        meta_path = project_root / "experiments" / "configs" / "meta.yaml"
        with open(meta_path) as f:
            meta = yaml.safe_load(f) or {}

        tools = meta.get("tools", {})

        if not tools:
            console.print("[yellow]No tools in this project[/yellow]")
            console.print("[dim]Add tools with: expaper tool add <name>[/dim]")
            return

        table = Table(title="Project Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="dim")
        table.add_column("Entrypoint")

        for name, info in sorted(tools.items()):
            table.add_row(
                name,
                info.get("path", ""),
                info.get("entrypoint", ""),
            )

        console.print(table)
