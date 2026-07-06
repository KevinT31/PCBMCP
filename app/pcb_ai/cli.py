"""CLI del pipeline pcb-ai."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from pcb_ai import __version__
from pcb_ai.tools import discover_all, write_tools_yaml

app = typer.Typer(
    name="pcb-ai",
    help="Pipeline agéntico de EDA: requisitos → esquemático → ERC → PCB → DRC → fabricación.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version() -> None:
    """Muestra la versión de pcb-ai."""
    console.print(f"pcb-ai {__version__}")


@app.command()
def doctor(
    write: bool = typer.Option(
        True, "--write/--no-write", help="Persistir lo descubierto en config/tools.yaml"
    ),
) -> None:
    """Diagnostica el entorno: descubre herramientas y verifica que respondan."""
    tools = discover_all()

    table = Table(title="pcb-ai doctor — estado del entorno")
    table.add_column("Herramienta")
    table.add_column("Estado")
    table.add_column("Versión")
    table.add_column("Ruta / notas", overflow="fold")

    status_style = {"OK": "green", "MISSING": "red", "BROKEN": "yellow"}
    missing_required = []
    for t in tools:
        style = status_style[t.status]
        required_mark = " (requerida)" if t.required and t.status != "OK" else ""
        notes = "; ".join(filter(None, [t.path, *t.notes]))
        table.add_row(
            t.name,
            f"[{style}]{t.status}{required_mark}[/{style}]",
            t.version or "—",
            notes or "—",
        )
        if t.required and t.status != "OK":
            missing_required.append(t.name)

    console.print(table)

    if write:
        path = write_tools_yaml(tools)
        console.print(f"[dim]Descubrimiento guardado en {path}[/dim]")

    if missing_required:
        console.print(
            f"[red]Faltan herramientas requeridas: {', '.join(missing_required)}[/red]"
        )
        raise typer.Exit(code=1)
    console.print("[green]Entorno base OK.[/green]")


if __name__ == "__main__":
    app()
