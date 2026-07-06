"""CLI del pipeline pcb-ai."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from pathlib import Path

from pcb_ai import __version__
from pcb_ai.tools import PROJECT_ROOT, discover_all, write_tools_yaml

app = typer.Typer(
    name="pcb-ai",
    help="Pipeline agéntico de EDA: requisitos → esquemático → ERC → PCB → DRC → fabricación.",
    no_args_is_help=True,
)
spec_app = typer.Typer(help="Validación y schema de la especificación de diseño.")
app.add_typer(spec_app, name="spec")
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


@spec_app.command("validate")
def spec_validate(
    path: Path = typer.Argument(
        Path("spec/design_spec.yaml"), help="Ruta al design_spec.yaml"
    ),
) -> None:
    """Valida la especificación de diseño contra el schema y las reglas cruzadas."""
    from pydantic import ValidationError

    from pcb_ai.spec import load_spec

    target = path if path.is_absolute() else PROJECT_ROOT / path
    if not target.exists():
        console.print(f"[red]No existe: {target}[/red]")
        raise typer.Exit(code=2)
    try:
        spec = load_spec(target)
    except ValidationError as exc:
        console.print(f"[red]Spec inválida ({exc.error_count()} errores):[/red]")
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            console.print(f"  [yellow]{loc or '(raíz)'}[/yellow]: {err['msg']}")
        raise typer.Exit(code=1)
    except ValueError as exc:
        console.print(f"[red]Spec inválida:[/red] {exc}")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Spec válida:[/green] {spec.project.name} rev {spec.project.revision} — "
        f"{len(spec.power_rails)} rails, {len(spec.functional_blocks)} bloques, "
        f"{len(spec.critical_nets)} nets críticas"
    )


@spec_app.command("schema")
def spec_schema(
    out: Path = typer.Option(Path("spec/schema.json"), help="Archivo de salida"),
) -> None:
    """Exporta el JSON Schema de la especificación de diseño."""
    import json

    from pcb_ai.spec import export_json_schema

    target = out if out.is_absolute() else PROJECT_ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(export_json_schema(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    console.print(f"[green]Schema exportado a {target}[/green]")


if __name__ == "__main__":
    app()
