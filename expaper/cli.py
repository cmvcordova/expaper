"""CLI entry point for expaper."""

import click
from rich.console import Console

from expaper import __version__
from expaper.scaffold import create_project
from expaper.tools import add_tool_to_project, list_registry_tools
from expaper.overleaf import sync_pull, sync_push, sync_status, link_overleaf

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """expaper - Research project scaffolding tool.

    Combines experimentStash structure with Overleaf integration
    for reproducible research projects.
    """
    pass


@main.command()
@click.argument("name")
@click.option("--path", "-p", default=".", help="Parent directory for project")
@click.option("--tools", "-t", multiple=True, help="Tools to add (registry name or URL)")
@click.option("--overleaf", "-o", help="Overleaf Git URL to link")
@click.option("--template", default="blank", help="Paper template (icml2026, neurips2025, arxiv, blank)")
@click.option("--dry-run", is_flag=True, help="Show what would be created without creating")
def init(name: str, path: str, tools: tuple, overleaf: str, template: str, dry_run: bool):
    """Create a new research project.

    Example:
        expaper init my-research --tools geomancy --overleaf https://git.overleaf.com/xxx
    """
    create_project(
        name=name,
        parent_path=path,
        tools=list(tools),
        overleaf_url=overleaf,
        template=template,
        dry_run=dry_run,
    )


@main.group()
def tool():
    """Manage experiment tools."""
    pass


@tool.command("add")
@click.argument("name")
@click.argument("url", required=False)
@click.option("--entrypoint", "-e", help="Tool entrypoint (e.g., '-m tool.main')")
@click.option("--description", "-d", help="Tool description")
def tool_add(name: str, url: str, entrypoint: str, description: str):
    """Add a tool to the current project.

    Examples:
        expaper tool add geomancy              # From registry
        expaper tool add mytool https://github.com/x/y  # From URL
    """
    add_tool_to_project(name, url, entrypoint, description)


@tool.command("list")
@click.option("--registry", "-r", is_flag=True, help="Show available tools in registry")
def tool_list(registry: bool):
    """List tools in current project or registry."""
    list_registry_tools(show_registry=registry)


@main.group()
def sync():
    """Sync with Overleaf."""
    pass


@sync.command("pull")
@click.option("--squash/--no-squash", default=True, help="Squash commits when pulling")
def sync_pull_cmd(squash: bool):
    """Pull changes from Overleaf."""
    sync_pull(squash=squash)


@sync.command("push")
def sync_push_cmd():
    """Push changes to Overleaf."""
    sync_push()


@sync.command("status")
def sync_status_cmd():
    """Show Overleaf sync status."""
    sync_status()


@main.command("link-overleaf")
@click.argument("url")
def link_overleaf_cmd(url: str):
    """Link an existing Overleaf project.

    Use this after creating a project without --overleaf flag.
    """
    link_overleaf(url)


@main.group()
def template():
    """Manage paper templates."""
    pass


@template.command("list")
def template_list():
    """List available paper templates."""
    from expaper.templates import list_templates
    list_templates()


@template.command("create")
@click.argument("name")
def template_create(name: str):
    """Create paper/ directory from a template."""
    from expaper.templates import create_from_template
    create_from_template(name)


@template.command("export")
@click.option("--output", "-o", default="paper.zip", help="Output ZIP filename")
def template_export(output: str):
    """Export paper/ as ZIP for Overleaf import."""
    from expaper.templates import export_paper_zip
    export_paper_zip(output)


if __name__ == "__main__":
    main()
