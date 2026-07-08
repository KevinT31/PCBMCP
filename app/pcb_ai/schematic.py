"""Generador de esquemáticos: modelo declarativo → .kicad_sch (KiCad 10).

Implementa las reglas de docs/architecture.md §1-2:

- kicad-sch-api SOLO en modo creación (TESTED, reports/smoke/kicad_sch_api_roundtrip.md):
  cada emisión re-crea el archivo completo desde el modelo; nunca se parchea in-place.
- Hash-guard: el SHA-256 de cada archivo emitido se persiste en build/emitted.sha256.
  Antes de re-emitir se compara contra el disco; si difieren se aborta — nunca se
  sobreescribe trabajo manual sin --force explícito.
- Regla de escritor único: si existe el lockfile de KiCad (~<archivo>.kicad_sch.lck)
  se aborta: la GUI tiene el archivo abierto.

La conectividad se expresa con labels locales anclados al pin (posición exacta del
pin calculada por la librería), no con wires punto a punto: el netlist queda definido
por nombre de net, que es el contrato que verify-spec comprueba.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from pcb_ai.tools import PROJECT_ROOT, _find_kicad_bin_dir

HASH_REGISTRY = PROJECT_ROOT / "build" / "emitted.sha256"


class EmitError(RuntimeError):
    """Fallo de emisión con causa accionable para el operador."""


@dataclass(frozen=True)
class Part:
    """Un componente del modelo con su conectividad por número de pin."""

    reference: str
    lib_id: str
    value: str
    position: tuple[float, float]
    footprint: str | None = None
    rotation: float = 0.0
    # pin number → nombre de net (label local anclado al pin)
    pins: Mapping[str, str] = field(default_factory=dict)
    # pines marcados explícitamente como no conectados
    nc_pins: tuple[str, ...] = ()
    # propiedades extra del símbolo (MPN, LCSC, ...)
    properties: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Note:
    """Texto libre en el esquemático (títulos de bloque, notas de diseño)."""

    text: str
    position: tuple[float, float]
    size: float = 2.0


@dataclass(frozen=True)
class BoardModel:
    name: str
    revision: str
    parts: tuple[Part, ...]
    notes: tuple[Note, ...] = ()

    def nets(self) -> set[str]:
        return {net for part in self.parts for net in part.pins.values()}

    def part(self, reference: str) -> Part:
        for p in self.parts:
            if p.reference == reference:
                return p
        raise KeyError(reference)

    def validate(self) -> list[str]:
        """Chequeos internos del modelo (no eléctricos: eso es del ERC)."""
        problems: list[str] = []
        refs = [p.reference for p in self.parts]
        for ref in {r for r in refs if refs.count(r) > 1}:
            problems.append(f"referencia duplicada: {ref}")
        for part in self.parts:
            overlap = set(part.pins) & set(part.nc_pins)
            if overlap:
                problems.append(
                    f"{part.reference}: pines a la vez conectados y NC: {sorted(overlap)}"
                )
            if not part.lib_id.count(":") == 1:
                problems.append(f"{part.reference}: lib_id inválido: {part.lib_id}")
            for coord in part.position:
                # pines fuera del grid de 1.27 mm no conectan con labels/wires
                if round(coord / 1.27, 6) % 1 != 0:
                    problems.append(
                        f"{part.reference}: posición {part.position} fuera del grid 1.27 mm"
                    )
                    break
        return problems


@dataclass(frozen=True)
class EmitResult:
    schematic: Path
    project: Path
    sha256: dict[str, str]


def kicad_share_dir() -> Path | None:
    bin_dir = _find_kicad_bin_dir()
    if bin_dir is None:
        return None
    share = bin_dir.parents[0] / "share" / "kicad"
    return share if share.is_dir() else None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel_key(target: Path) -> str:
    """Clave del registro: ruta relativa al repo, o absoluta si cae fuera (tests)."""
    try:
        return target.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return target.as_posix()


def _load_registry() -> dict[str, str]:
    if not HASH_REGISTRY.exists():
        return {}
    entries: dict[str, str] = {}
    for line in HASH_REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            digest, _, rel = line.partition("  ")
            if rel:
                entries[rel] = digest
    return entries


def _save_registry(entries: dict[str, str]) -> None:
    HASH_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# SHA-256 de archivos emitidos por pcb-ai generate (hash-guard)"]
    lines += [f"{digest}  {rel}" for rel, digest in sorted(entries.items())]
    HASH_REGISTRY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _guard_before_emit(targets: list[Path], force: bool) -> None:
    """Hash-guard + lockfile (architecture.md §1 reglas 3 y 4)."""
    for target in targets:
        lock = target.parent / f"~{target.name}.lck"
        if lock.exists():
            raise EmitError(
                f"KiCad tiene abierto {target.name} (lockfile {lock.name}); "
                "cerrar la GUI antes de emitir (regla de escritor único)"
            )
    registry = _load_registry()
    for target in targets:
        if not target.exists():
            continue
        rel = _rel_key(target)
        recorded = registry.get(rel)
        actual = _sha256(target)
        if recorded is None:
            if not force:
                raise EmitError(
                    f"{rel} existe pero no fue emitido por el generador "
                    "(sin registro en build/emitted.sha256); usar --force para sobreescribir"
                )
        elif recorded != actual:
            if not force:
                raise EmitError(
                    f"{rel} fue modificado fuera del generador desde la última emisión "
                    "(hash-guard); revisar el cambio o usar --force para descartarlo"
                )


_KICAD_PRO_MINIMAL = {
    "board": {"design_settings": {}, "layer_presets": [], "viewports": []},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "", "version": 3},
    "net_settings": {"classes": []},
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
    "sheets": [],
    "text_variables": {},
}


def emit(model: BoardModel, out_dir: Path, force: bool = False) -> EmitResult:
    """Emite el proyecto KiCad completo desde el modelo (modo creación puro)."""
    problems = model.validate()
    if problems:
        raise EmitError("modelo inválido: " + "; ".join(problems))

    share = kicad_share_dir()
    if share is not None:
        os.environ.setdefault("KICAD_SYMBOL_DIR", str(share / "symbols"))

    import kicad_sch_api as ksa
    from kicad_sch_api.core.pin_utils import get_component_pin_position

    out_dir = out_dir if out_dir.is_absolute() else PROJECT_ROOT / out_dir
    sch_path = out_dir / f"{model.name}.kicad_sch"
    pro_path = out_dir / f"{model.name}.kicad_pro"
    _guard_before_emit([sch_path, pro_path], force=force)
    out_dir.mkdir(parents=True, exist_ok=True)

    sch = ksa.create_schematic(model.name)

    for part in model.parts:
        comp = sch.components.add(
            part.lib_id,
            reference=part.reference,
            value=part.value,
            position=part.position,
            footprint=part.footprint,
            rotation=part.rotation,
            **dict(part.properties),
        )
        for pin_number, net in part.pins.items():
            sch.add_label(net, pin=(part.reference, pin_number))
        for pin_number in part.nc_pins:
            pos = get_component_pin_position(comp._data, pin_number)
            if pos is None:
                raise EmitError(
                    f"{part.reference}: pin NC {pin_number} no existe en {part.lib_id}"
                )
            sch.no_connects.add((pos.x, pos.y))

    for note in model.notes:
        sch.add_text(note.text, position=note.position, size=note.size)

    sch.save_as(str(sch_path))

    pro = dict(_KICAD_PRO_MINIMAL)
    pro["meta"] = {"filename": pro_path.name, "version": 3}
    pro_path.write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")

    registry = _load_registry()
    shas: dict[str, str] = {}
    for target in (sch_path, pro_path):
        rel = _rel_key(target)
        digest = _sha256(target)
        registry[rel] = digest
        shas[rel] = digest
    _save_registry(registry)

    return EmitResult(schematic=sch_path, project=pro_path, sha256=shas)
