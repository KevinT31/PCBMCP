"""Volcado de pines (número, nombre, tipo eléctrico) de los símbolos KiCad usados
por demo-vigia, leyendo las librerías oficiales instaladas.

Uso: uv run python scripts/dump_symbol_pins.py
Sirve para cotejar el mapa pin→net del modelo contra la librería real antes de
generar (regla del proyecto: ninguna conexión sin verificar el símbolo).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "app"))

from pcb_ai.tools import _find_kicad_bin_dir  # noqa: E402

LIB_IDS = [
    "Connector:USB_C_Receptacle_USB2.0_16P",
    "Device:Polyfuse_Small",
    "Diode:SMF5V0A",
    "Regulator_Linear:AP2112K-3.3",
    "MCU_ST_STM32G0:STM32G030F6Px",
    "Sensor_Temperature:LM75B",
    "Connector_Generic:Conn_01x05",
    "Device:R",
    "Device:C",
    "Device:LED",
    "Switch:SW_Push",
    "Connector:TestPoint",
    "power:PWR_FLAG",
    "power:GND",
    "power:+3V3",
    "Mechanical:MountingHole",
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    kicad_bin = _find_kicad_bin_dir()
    if kicad_bin is None:
        print("KiCad no encontrado")
        return 1
    symbols_dir = kicad_bin.parents[0] / "share" / "kicad" / "symbols"
    os.environ.setdefault("KICAD_SYMBOL_DIR", str(symbols_dir))

    import kicad_sch_api as ksa
    from kicad_sch_api.core.pin_utils import list_component_pins

    sch = ksa.create_schematic("pin_dump")
    x = 0.0
    for lib_id in LIB_IDS:
        try:
            comp = sch.components.add(lib_id, position=(50 + x, 50), value=lib_id)
            x += 30
        except Exception as exc:  # noqa: BLE001 — inspección: reportar y seguir
            print(f"\n## {lib_id}: ERROR {type(exc).__name__}: {exc}")
            continue
        print(f"\n## {lib_id} (ref {comp.reference})")
        try:
            raw = comp._data  # SchematicSymbol subyacente
            pins = list_component_pins(raw)
            seen = set()
            for num, pos in pins:
                if num in seen:
                    continue
                seen.add(num)
                print(f"  pin {num}: abs=({pos.x:.2f},{pos.y:.2f})")
        except Exception as exc:  # noqa: BLE001
            print(f"  (sin detalle de pines: {type(exc).__name__}: {exc})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
