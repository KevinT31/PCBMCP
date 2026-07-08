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


@app.command()
def generate(
    force: bool = typer.Option(
        False,
        "--force",
        help="Sobreescribir aunque el hash-guard detecte ediciones externas",
    ),
    out: Path = typer.Option(
        Path("hardware/demo-vigia"), help="Directorio de salida del proyecto KiCad"
    ),
) -> None:
    """Emite el proyecto KiCad de demo-vigia desde el modelo (handoff spec → KiCad)."""
    from pcb_ai.boards.demo_vigia import CONTRACT_NETS, build_model
    from pcb_ai.schematic import EmitError, emit

    model = build_model()
    try:
        result = emit(model, out, force=force)
    except EmitError as exc:
        console.print(f"[red]Emisión abortada:[/red] {exc}")
        raise typer.Exit(code=1)

    nets = model.nets()
    missing = CONTRACT_NETS - nets
    console.print(
        f"[green]Emitido[/green] {model.name} rev {model.revision}: "
        f"{len(model.parts)} componentes, {len(nets)} nets"
    )
    for rel, digest in result.sha256.items():
        console.print(f"  [dim]{rel}  sha256={digest[:12]}…[/dim]")
    if missing:
        console.print(f"[red]Nets del contrato ausentes: {sorted(missing)}[/red]")
        raise typer.Exit(code=1)
    console.print("[dim]Contrato de nets completo. Siguiente paso: pcb-ai run-erc[/dim]")


@app.command("run-erc")
def run_erc(
    sch: Path = typer.Argument(
        Path("hardware/demo-vigia/demo-vigia.kicad_sch"), help="Esquemático a verificar"
    ),
    report: Path = typer.Option(
        None,
        "--report",
        help="Ruta del JSON de salida (default: reports/erc/<nombre>_erc.json)",
    ),
) -> None:
    """Corre kicad-cli sch erc (JSON) y resume las violaciones. Exit 1 si hay alguna."""
    import json
    import subprocess

    from pcb_ai.tools import _load_config_paths, discover_tool

    sch_path = sch if sch.is_absolute() else PROJECT_ROOT / sch
    if not sch_path.exists():
        console.print(f"[red]No existe: {sch_path}[/red]")
        raise typer.Exit(code=2)

    kicad_cli = discover_tool("kicad-cli", required=True, config_paths=_load_config_paths())
    if kicad_cli.status != "OK":
        console.print("[red]kicad-cli no disponible (ver pcb-ai doctor)[/red]")
        raise typer.Exit(code=2)

    report_path = (
        report
        if report is not None
        else PROJECT_ROOT / "reports" / "erc" / f"{sch_path.stem}_erc.json"
    )
    report_path = report_path if report_path.is_absolute() else PROJECT_ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.exists():
        report_path.unlink()  # nunca leer un reporte viejo si kicad-cli falla

    result = subprocess.run(
        [
            kicad_cli.path,
            "sch",
            "erc",
            "--format",
            "json",
            "--output",
            str(report_path),
            str(sch_path),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if not report_path.exists():
        console.print(f"[red]kicad-cli no generó el reporte (exit {result.returncode}):[/red]")
        console.print((result.stderr or result.stdout).strip())
        raise typer.Exit(code=2)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    violations = [v for sheet in data.get("sheets", []) for v in sheet.get("violations", [])]

    # Se cuentan violaciones PRE-exclusion (regla anti-trampa del loop ERC)
    by_severity: dict[str, int] = {}
    table = Table(title=f"ERC — {sch_path.name} ({len(violations)} violaciones)")
    table.add_column("Severidad")
    table.add_column("Tipo")
    table.add_column("Descripción", overflow="fold")
    table.add_column("Posición")
    for v in violations:
        sev = v.get("severity", "?")
        by_severity[sev] = by_severity.get(sev, 0) + 1
        item = (v.get("items") or [{}])[0]
        pos = item.get("pos") or {}
        pos_txt = f"({pos.get('x', '?')}, {pos.get('y', '?')})" if pos else "—"
        table.add_row(sev, v.get("type", "?"), v.get("description", "?"), pos_txt)

    console.print(table)
    console.print(f"[dim]Reporte: {report_path}[/dim]")
    if violations:
        resumen = ", ".join(f"{n} {s}" for s, n in sorted(by_severity.items()))
        console.print(f"[red]ERC NO verde: {resumen}[/red]")
        raise typer.Exit(code=1)
    console.print("[green]ERC verde: 0 violaciones.[/green]")


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
