"""Overleaf integration via git subtree."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def find_project_root() -> Optional[Path]:
    """Find the project root (directory with experiments/ and paper/)."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "experiments").exists() or (parent / "paper").exists():
            return parent
    return None


def get_overleaf_remote() -> Optional[str]:
    """Get the Overleaf remote URL if configured."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "overleaf"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def has_paper_directory() -> bool:
    """Check if paper/ directory exists."""
    project_root = find_project_root()
    if project_root:
        return (project_root / "paper").exists()
    return False


def sync_pull(squash: bool = True) -> None:
    """Pull changes from Overleaf.

    Args:
        squash: Whether to squash commits (default: True)
    """
    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        raise SystemExit(1)

    overleaf_url = get_overleaf_remote()
    if not overleaf_url:
        console.print("[red]Error:[/red] No Overleaf remote configured")
        console.print("[dim]Link Overleaf with: expaper link-overleaf <url>[/dim]")
        raise SystemExit(1)

    if not has_paper_directory():
        console.print("[red]Error:[/red] No paper/ directory found")
        raise SystemExit(1)

    console.print("[cyan]Pulling from Overleaf...[/cyan]")

    cmd = ["git", "subtree", "pull", "--prefix=paper", "overleaf", "master"]
    if squash:
        cmd.append("--squash")

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode != 0:
        console.print("[red]Error pulling from Overleaf[/red]")
        console.print("[dim]You may need to resolve merge conflicts[/dim]")
        raise SystemExit(1)

    console.print("[green]Successfully pulled from Overleaf[/green]")


def sync_push() -> None:
    """Push changes to Overleaf."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        raise SystemExit(1)

    overleaf_url = get_overleaf_remote()
    if not overleaf_url:
        console.print("[red]Error:[/red] No Overleaf remote configured")
        console.print("[dim]Link Overleaf with: expaper link-overleaf <url>[/dim]")
        raise SystemExit(1)

    if not has_paper_directory():
        console.print("[red]Error:[/red] No paper/ directory found")
        raise SystemExit(1)

    # Check for uncommitted changes in paper/
    result = subprocess.run(
        ["git", "status", "--porcelain", "paper/"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        console.print("[yellow]Warning:[/yellow] Uncommitted changes in paper/")
        console.print("[dim]Commit your changes first:[/dim]")
        console.print("[dim]  git add paper/ && git commit -m 'Update paper'[/dim]")
        raise SystemExit(1)

    console.print("[cyan]Pushing to Overleaf...[/cyan]")

    result = subprocess.run(
        ["git", "subtree", "push", "--prefix=paper", "overleaf", "master"],
        cwd=project_root,
    )

    if result.returncode != 0:
        console.print("[red]Error pushing to Overleaf[/red]")
        console.print("[dim]Check your credentials and try again[/dim]")
        raise SystemExit(1)

    console.print("[green]Successfully pushed to Overleaf[/green]")


def sync_status() -> None:
    """Show Overleaf sync status."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        raise SystemExit(1)

    console.print("[bold]Overleaf Sync Status[/bold]\n")

    # Check remote
    overleaf_url = get_overleaf_remote()
    if overleaf_url:
        console.print(f"  Remote: [cyan]{overleaf_url}[/cyan]")
    else:
        console.print("  Remote: [red]Not configured[/red]")
        console.print("  [dim]Link with: expaper link-overleaf <url>[/dim]")
        return

    # Check paper directory
    if has_paper_directory():
        console.print("  Paper directory: [green]exists[/green]")
    else:
        console.print("  Paper directory: [red]missing[/red]")
        return

    # Check for local changes
    result = subprocess.run(
        ["git", "status", "--porcelain", "paper/"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        console.print("  Local changes: [yellow]uncommitted[/yellow]")
        for line in result.stdout.strip().split("\n"):
            console.print(f"    {line}")
    else:
        console.print("  Local changes: [green]none[/green]")

    # Fetch and check for remote changes
    console.print("\n[dim]Fetching from Overleaf...[/dim]")
    subprocess.run(
        ["git", "fetch", "overleaf"],
        cwd=project_root,
        capture_output=True,
    )

    # This is a rough check - subtree makes this complex
    console.print("\n[dim]To check for remote changes, run:[/dim]")
    console.print("[dim]  expaper sync pull --dry-run[/dim]")


def link_overleaf(url: str) -> None:
    """Link an existing Overleaf project.

    Args:
        url: Overleaf Git URL (https://git.overleaf.com/...)
    """
    project_root = find_project_root()
    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        raise SystemExit(1)

    # Validate URL format
    if not url.startswith("https://git.overleaf.com/"):
        console.print("[yellow]Warning:[/yellow] URL doesn't look like an Overleaf Git URL")
        console.print("[dim]Expected format: https://git.overleaf.com/<project-id>[/dim]")

    # Check if already configured
    existing = get_overleaf_remote()
    if existing:
        console.print(f"[yellow]Warning:[/yellow] Overleaf remote already configured: {existing}")
        console.print("[dim]Remove with: git remote remove overleaf[/dim]")
        raise SystemExit(1)

    # Check for existing paper directory with content
    paper_dir = project_root / "paper"
    if paper_dir.exists() and any(paper_dir.iterdir()):
        console.print("[red]Error:[/red] paper/ directory is not empty")
        console.print("[dim]Remove or backup existing content first[/dim]")
        raise SystemExit(1)

    # Remove empty paper directory if exists
    if paper_dir.exists():
        shutil.rmtree(paper_dir)

    # Ensure we have a clean working tree
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        console.print("[yellow]Warning:[/yellow] Uncommitted changes detected")
        console.print("[dim]Committing current state before linking...[/dim]")
        subprocess.run(["git", "add", "."], cwd=project_root)
        subprocess.run(
            ["git", "commit", "-m", "Pre-Overleaf link state"],
            cwd=project_root,
            capture_output=True,
        )

    console.print(f"[cyan]Linking Overleaf project...[/cyan]")

    # Add remote
    result = subprocess.run(
        ["git", "remote", "add", "overleaf", url],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]Error adding remote:[/red] {result.stderr}")
        raise SystemExit(1)

    # Fetch
    console.print("[dim]Fetching from Overleaf (credentials may be required)...[/dim]")
    result = subprocess.run(
        ["git", "fetch", "overleaf"],
        cwd=project_root,
    )
    if result.returncode != 0:
        console.print("[red]Error fetching from Overleaf[/red]")
        subprocess.run(["git", "remote", "remove", "overleaf"], cwd=project_root)
        raise SystemExit(1)

    # Add subtree
    result = subprocess.run(
        ["git", "subtree", "add", "--prefix=paper", "overleaf", "master", "--squash"],
        cwd=project_root,
    )
    if result.returncode != 0:
        console.print("[red]Error adding subtree[/red]")
        subprocess.run(["git", "remote", "remove", "overleaf"], cwd=project_root)
        raise SystemExit(1)

    console.print("[green]Overleaf project linked successfully![/green]")
    console.print("\n[dim]Sync commands:[/dim]")
    console.print("  expaper sync pull   # Get collaborator changes")
    console.print("  expaper sync push   # Push your changes")
