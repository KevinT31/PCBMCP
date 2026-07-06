"""Modelos de la especificación de diseño (spec/design_spec.yaml).

Principios:
- Campos críticos EXPLÍCITOS: sin defaults silenciosos para decisiones eléctricas.
- `extra="forbid"`: un typo en un campo es un error, no un campo ignorado.
- Validación cruzada: cada rail debe tener fuente definida, las nets críticas
  deben tener clase, las simulaciones requeridas deben referenciar bloques existentes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Project(StrictModel):
    name: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    purpose: str = Field(min_length=1)


class VoltageRange(StrictModel):
    min_v: float
    max_v: float

    @model_validator(mode="after")
    def _order(self) -> "VoltageRange":
        if self.min_v >= self.max_v:
            raise ValueError("min_v debe ser menor que max_v")
        return self


class PowerInput(StrictModel):
    name: str
    connector: str
    voltage_nominal_v: float
    voltage_range: VoltageRange
    max_current_a: float = Field(gt=0)
    protection: list[str] = Field(
        default_factory=list,
        description="Protecciones requeridas, p.ej. ESD, inversión de polaridad, sobrecorriente",
    )


class PowerRail(StrictModel):
    name: str
    voltage_v: float
    tolerance_pct: float = Field(gt=0, le=20)
    max_current_a: float = Field(gt=0)
    source: str = Field(
        description="Nombre del power input o del bloque regulador que genera este rail"
    )


class Interface(StrictModel):
    name: str
    type: Literal[
        "usb2_fs", "usb2_hs", "i2c", "spi", "uart", "swd", "jtag",
        "gpio", "analog_in", "pwm", "can", "onewire", "other",
    ]
    connector: str | None = None
    speed: str | None = None
    notes: str | None = None


class FunctionalBlock(StrictModel):
    name: str
    purpose: str
    interfaces: list[str] = Field(default_factory=list)
    notes: str | None = None


class BoardConstraints(StrictModel):
    max_width_mm: float = Field(gt=0)
    max_height_mm: float = Field(gt=0)
    layers: Literal[1, 2, 4, 6]


class Constraints(StrictModel):
    board: BoardConstraints
    electrical: list[str] = Field(default_factory=list)
    mechanical: list[str] = Field(default_factory=list)


class CriticalNet(StrictModel):
    name: str
    net_class: Literal[
        "power_critical", "high_current", "differential", "clock",
        "analog_sensitive", "switching",
    ]
    rules: str = Field(description="Regla de diseño explícita para esta net")


class Manufacturing(StrictModel):
    target_fab: str
    assembly: Literal["manual", "smt_service", "mixed"]
    min_trace_mm: float = Field(gt=0)
    min_clearance_mm: float = Field(gt=0)
    min_drill_mm: float = Field(gt=0)


class Verification(StrictModel):
    required_simulations: list[str] = Field(default_factory=list)
    required_tests: list[str] = Field(default_factory=list)


class DesignSpec(StrictModel):
    project: Project
    power_inputs: list[PowerInput] = Field(min_length=1)
    power_rails: list[PowerRail] = Field(min_length=1)
    interfaces: list[Interface] = Field(default_factory=list)
    functional_blocks: list[FunctionalBlock] = Field(min_length=1)
    constraints: Constraints
    critical_nets: list[CriticalNet] = Field(default_factory=list)
    component_preferences: list[str] = Field(default_factory=list)
    forbidden_components: list[str] = Field(default_factory=list)
    manufacturing: Manufacturing
    verification: Verification

    @model_validator(mode="after")
    def _cross_checks(self) -> "DesignSpec":
        input_names = {p.name for p in self.power_inputs}
        block_names = {b.name for b in self.functional_blocks}
        rail_names = {r.name for r in self.power_rails}

        errors: list[str] = []
        for rail in self.power_rails:
            if rail.source not in input_names | block_names:
                errors.append(
                    f"rail '{rail.name}': source '{rail.source}' no es un power input "
                    f"ni un bloque funcional definido"
                )
        iface_names = {i.name for i in self.interfaces}
        for block in self.functional_blocks:
            for iface in block.interfaces:
                if iface not in iface_names:
                    errors.append(
                        f"bloque '{block.name}': interfaz '{iface}' no está definida"
                    )
        for sim in self.verification.required_simulations:
            if sim not in block_names:
                errors.append(
                    f"simulación requerida '{sim}' no corresponde a ningún bloque funcional"
                )
        dup = [n for n in rail_names if sum(1 for r in self.power_rails if r.name == n) > 1]
        if dup:
            errors.append(f"rails duplicados: {sorted(set(dup))}")

        if errors:
            raise ValueError("; ".join(errors))
        return self


def load_spec(path: Path) -> DesignSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} no contiene un mapeo YAML válido")
    return DesignSpec.model_validate(data)


def export_json_schema() -> dict:
    return DesignSpec.model_json_schema()
