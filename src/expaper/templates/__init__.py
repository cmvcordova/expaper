"""Template management for expaper."""

import shutil
import zipfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

TEMPLATES_DIR = Path(__file__).parent


def get_available_templates() -> list[str]:
    """Get list of available paper templates."""
    paper_dir = TEMPLATES_DIR / "paper"
    if not paper_dir.exists():
        return []
    return [d.name for d in paper_dir.iterdir() if d.is_dir()]


def list_templates() -> None:
    """List available paper templates."""
    templates = get_available_templates()

    if not templates:
        console.print("[yellow]No paper templates available[/yellow]")
        return

    table = Table(title="Available Paper Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    descriptions = {
        "blank": "Minimal LaTeX document for local-first workflows",
    }

    for name in sorted(templates):
        table.add_row(name, descriptions.get(name, ""))

    console.print(table)
    console.print("\n[dim]For conference templates (ICML, NeurIPS, ICLR), use Overleaf's gallery:[/dim]")
    console.print("[dim]  1. Create project from template at overleaf.com/gallery[/dim]")
    console.print("[dim]  2. Link with: expaper link-overleaf <url>[/dim]")


def create_from_template(template_name: str) -> None:
    """Create paper/ directory from a template.

    Args:
        template_name: Name of the template to use
    """
    # Find project root
    cwd = Path.cwd()
    project_root = None
    for parent in [cwd] + list(cwd.parents):
        if (parent / "experiments").exists():
            project_root = parent
            break

    if not project_root:
        console.print("[red]Error:[/red] Not in an expaper project directory")
        raise SystemExit(1)

    paper_dir = project_root / "paper"
    if paper_dir.exists() and any(paper_dir.iterdir()):
        console.print("[red]Error:[/red] paper/ directory is not empty")
        console.print("[dim]Remove existing content first or use a different approach[/dim]")
        raise SystemExit(1)

    template_dir = TEMPLATES_DIR / "paper" / template_name
    if not template_dir.exists():
        console.print(f"[red]Error:[/red] Template '{template_name}' not found")
        console.print("[dim]Available templates:[/dim]")
        for t in get_available_templates():
            console.print(f"  - {t}")
        raise SystemExit(1)

    # Create paper directory
    paper_dir.mkdir(exist_ok=True)

    # Copy template files
    for item in template_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, paper_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, paper_dir / item.name)

    console.print(f"[green]Created paper/ from template '{template_name}'[/green]")
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  1. Edit paper/main.tex")
    console.print("  2. Upload to Overleaf or link existing project")
    console.print("  3. expaper link-overleaf <url>")


def export_paper_zip(output: str = "paper.zip") -> None:
    """Export paper/ directory as ZIP for Overleaf import.

    Args:
        output: Output filename
    """
    # Find project root
    cwd = Path.cwd()
    project_root = None
    for parent in [cwd] + list(cwd.parents):
        if (parent / "paper").exists():
            project_root = parent
            break

    if not project_root:
        console.print("[red]Error:[/red] No paper/ directory found")
        raise SystemExit(1)

    paper_dir = project_root / "paper"
    if not any(paper_dir.iterdir()):
        console.print("[red]Error:[/red] paper/ directory is empty")
        raise SystemExit(1)

    output_path = Path(output)
    if output_path.exists():
        console.print(f"[yellow]Warning:[/yellow] Overwriting {output}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in paper_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(paper_dir)
                zf.write(file_path, arcname)

    console.print(f"[green]Exported to {output_path}[/green]")
    console.print("\n[dim]Upload this ZIP to Overleaf:[/dim]")
    console.print("  1. Go to overleaf.com")
    console.print("  2. Click 'New Project' -> 'Upload Project'")
    console.print(f"  3. Upload {output_path}")
