"""Smoke test: ¿kicad-sch-api es seguro con el formato KiCad 10?

Cierra el UNVERIFIED §9.1-2 de docs/research/kicad_automation_stack.md.

Prueba A (roundtrip): cargar un .kicad_sch generado por KiCad 10 y re-guardarlo.
  Éxito = kicad-cli lo sigue parseando, el ERC da las mismas violaciones y el
  diff textual es acotado (idealmente nulo).

Prueba B (creación): crear un esquemático desde cero con un componente y un wire.
  Éxito = kicad-cli sch erc corre sobre él sin error de parseo.

Salida: reports/smoke/kicad_sch_api_roundtrip.md
"""

from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SANDBOX = PROJECT / "sandbox" / "sch_api_smoke"
REPORT = PROJECT / "reports" / "smoke" / "kicad_sch_api_roundtrip.md"


def find_kicad_cli() -> Path:
    for root in (
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "KiCad",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "KiCad",
    ):
        if root.is_dir():
            for ver in sorted(root.iterdir(), reverse=True):
                cli = ver / "bin" / "kicad-cli.exe"
                if cli.exists():
                    return cli
    raise SystemExit("kicad-cli no encontrado")


def run_erc(cli: Path, sch: Path, out: Path) -> tuple[int, int]:
    """Devuelve (exit_code, num_violaciones). -1 si el reporte no se generó."""
    result = subprocess.run(
        [str(cli), "sch", "erc", "--format", "json", "--output", str(out), str(sch)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if not out.exists():
        return result.returncode, -1
    data = json.loads(out.read_text(encoding="utf-8"))
    count = sum(len(s.get("violations", [])) for s in data.get("sheets", []))
    return result.returncode, count


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cli = find_kicad_cli()
    kicad_share = cli.parents[1] / "share" / "kicad"
    # kicad-sch-api busca KICAD_SYMBOL_DIR / rutas por máquina; esta instalación es por usuario
    os.environ.setdefault("KICAD_SYMBOL_DIR", str(kicad_share / "symbols"))
    demo_sch = kicad_share / "demos" / "ecc83" / "ecc83-pp.kicad_sch"
    assert demo_sch.exists(), f"demo no encontrada: {demo_sch}"

    SANDBOX.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Smoke test kicad-sch-api vs formato KiCad 10", ""]
    ok = True

    # ---------- Prueba A: roundtrip ----------
    original = SANDBOX / "original.kicad_sch"
    shutil.copy(demo_sch, original)
    # copiar tablas de librería del demo para que el ERC resuelva símbolos igual
    for aux in ("sym-lib-table", "fp-lib-table", "ecc83-pp.kicad_pro", "ecc83-pp.kicad_sym"):
        src = demo_sch.parent / aux
        if src.exists():
            shutil.copy(src, SANDBOX / aux)

    import kicad_sch_api as ksa

    roundtrip = SANDBOX / "roundtrip.kicad_sch"
    try:
        sch = ksa.load_schematic(str(original))
        sch.save_as(str(roundtrip))
        lines.append("- Carga y re-guardado: **OK**")
    except Exception as exc:  # noqa: BLE001 — smoke test: reportar cualquier fallo
        lines.append(f"- Carga/re-guardado: **FALLO** — {type(exc).__name__}: {exc}")
        ok = False

    if roundtrip.exists():
        rc_orig, v_orig = run_erc(cli, original, SANDBOX / "erc_original.json")
        rc_rt, v_rt = run_erc(cli, roundtrip, SANDBOX / "erc_roundtrip.json")
        lines.append(f"- ERC original: exit={rc_orig}, violaciones={v_orig}")
        lines.append(f"- ERC roundtrip: exit={rc_rt}, violaciones={v_rt}")
        if v_rt == -1 or rc_rt not in (0,):
            lines.append("- **FALLO: el archivo re-guardado no es parseable por kicad-cli**")
            ok = False
        elif v_orig != v_rt:
            lines.append(
                f"- **ADVERTENCIA: el número de violaciones cambió ({v_orig} → {v_rt})** — "
                "el roundtrip altera semántica"
            )
            ok = False
        diff = list(
            difflib.unified_diff(
                original.read_text(encoding="utf-8").splitlines(),
                roundtrip.read_text(encoding="utf-8").splitlines(),
                lineterm="",
            )
        )
        changed = sum(1 for d in diff if d.startswith(("+", "-")) and not d.startswith(("+++", "---")))
        total = len(original.read_text(encoding="utf-8").splitlines())
        lines.append(f"- Diff textual: {changed} líneas cambiadas de {total}")

    # ---------- Prueba B: creación desde cero ----------
    lines.append("")
    created = SANDBOX / "created.kicad_sch"
    try:
        new_sch = ksa.create_schematic("smoke_created")
        r1 = new_sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        r2 = new_sch.components.add("Device:R", reference="R2", value="4.7k", position=(130, 100))
        new_sch.add_wire_between_pins("R1", "2", "R2", "1")
        new_sch.save_as(str(created))
        lines.append("- Creación desde cero (2 R + wire): **OK guardado**")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"- Creación desde cero: **FALLO** — {type(exc).__name__}: {exc}")
        ok = False

    if created.exists():
        rc_new, v_new = run_erc(cli, created, SANDBOX / "erc_created.json")
        parseable = rc_new == 0 and v_new >= 0
        lines.append(
            f"- ERC sobre el creado: exit={rc_new}, violaciones={v_new} → "
            f"{'**parseable por KiCad 10**' if parseable else '**NO parseable — FALLO**'}"
        )
        ok = ok and parseable

    lines.append("")
    lines.append(f"## Veredicto: {'APTO (TESTED)' if ok else 'NO APTO — usar fallback'}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
