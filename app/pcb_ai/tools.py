"""Descubrimiento de herramientas externas del pipeline.

Regla del proyecto: nunca hardcodear rutas de usuario. Se descubre en este orden:
1. config/tools.yaml (si el usuario fijó una ruta, manda).
2. PATH del sistema.
3. Ubicaciones de instalación conocidas (solo como candidatas, se verifica que existan).

Cada herramienta descubierta se verifica ejecutándola (--version o equivalente).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS_CONFIG = PROJECT_ROOT / "config" / "tools.yaml"


@dataclass
class ToolInfo:
    name: str
    required: bool
    path: str | None = None
    version: str | None = None
    status: str = "MISSING"  # OK | MISSING | BROKEN
    notes: list[str] = field(default_factory=list)


def _run_version(cmd: list[str], timeout: int = 30) -> str | None:
    """Ejecuta un comando de versión y devuelve la primera línea, o None si falla."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        out = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0 and out:
            return out.splitlines()[0].strip()
        return None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _load_config_paths() -> dict[str, str]:
    if not TOOLS_CONFIG.exists():
        return {}
    data = yaml.safe_load(TOOLS_CONFIG.read_text(encoding="utf-8")) or {}
    return {k: str(v) for k, v in (data.get("paths") or {}).items()}


def _find_kicad_bin_dir() -> Path | None:
    """Busca el directorio bin de la instalación de KiCad más reciente.

    Cubre instalación por máquina (Program Files) y por usuario (LOCALAPPDATA).
    """
    roots = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "KiCad",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "KiCad",
    ]
    candidates: list[Path] = []
    for root in roots:
        if root.is_dir():
            candidates.extend(
                d for d in root.iterdir() if d.is_dir() and (d / "bin").is_dir()
            )
    if not candidates:
        return None
    latest = max(candidates, key=lambda d: d.name)
    return latest / "bin"


def discover_tool(name: str, required: bool, config_paths: dict[str, str]) -> ToolInfo:
    info = ToolInfo(name=name, required=required)

    # 1. Ruta fijada en config/tools.yaml
    configured = config_paths.get(name)
    if configured:
        p = Path(configured)
        if p.exists():
            info.path = str(p)
            info.notes.append("ruta fijada en config/tools.yaml")
        else:
            info.status = "BROKEN"
            info.notes.append(f"config/tools.yaml apunta a ruta inexistente: {configured}")
            return info

    # 2. PATH
    if info.path is None:
        found = shutil.which(name)
        if found:
            info.path = found

    # 3. Ubicaciones conocidas
    if info.path is None:
        candidate = _known_location(name)
        if candidate:
            info.path = str(candidate)
            info.notes.append("encontrado fuera del PATH")

    if info.path is None:
        return info  # MISSING

    version = _version_of(name, info.path)
    if version is None:
        info.status = "BROKEN"
        info.notes.append("el ejecutable existe pero no respondió a la consulta de versión")
    else:
        info.status = "OK"
        info.version = version
    return info


def _known_location(name: str) -> Path | None:
    kicad_bin = _find_kicad_bin_dir()
    candidates: dict[str, list[Path]] = {
        "kicad-cli": [kicad_bin / "kicad-cli.exe"] if kicad_bin else [],
        "kicad-python": [kicad_bin / "python.exe"] if kicad_bin else [],
        "ngspice": [
            # ngspice_con.exe es la variante batch/consola; ngspice.exe abre GUI
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ngspice" / "Spice64" / "bin" / "ngspice_con.exe",
            Path(r"C:\Tools\ngspice\Spice64\bin\ngspice_con.exe"),
        ],
    }
    for path in candidates.get(name, []):
        if path.exists():
            return path
    return None


def _version_of(name: str, path: str) -> str | None:
    special = {
        "kicad-cli": [path, "version"],
        "kicad-python": [path, "-c", "import sys; print(sys.version.split()[0])"],
        "java": [path, "-version"],
        "ngspice": [path, "--version"],
    }
    cmd = special.get(name, [path, "--version"])
    return _run_version(cmd)


# Herramienta -> obligatoria para el pipeline base
PIPELINE_TOOLS: dict[str, bool] = {
    "python": True,
    "git": True,
    "kicad-cli": True,
    "kicad-python": False,  # Python embebido de KiCad (SWIG pcbnew)
    "ngspice": False,       # obligatoria solo para la fase de simulación
    "java": False,          # solo para FreeRouting (requiere Java 25)
    "uv": False,
}


def discover_all() -> list[ToolInfo]:
    config_paths = _load_config_paths()
    return [
        discover_tool(name, required, config_paths)
        for name, required in PIPELINE_TOOLS.items()
    ]


def write_tools_yaml(tools: list[ToolInfo]) -> Path:
    """Persiste lo descubierto en config/tools.yaml (sección `discovered`).

    La sección `paths` (overrides manuales del usuario) se preserva.
    """
    TOOLS_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    existing: dict = {}
    if TOOLS_CONFIG.exists():
        existing = yaml.safe_load(TOOLS_CONFIG.read_text(encoding="utf-8")) or {}
    existing["discovered"] = {
        t.name: {"path": t.path, "version": t.version, "status": t.status}
        for t in tools
    }
    existing.setdefault("paths", {})
    TOOLS_CONFIG.write_text(
        yaml.safe_dump(existing, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return TOOLS_CONFIG
