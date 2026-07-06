"""Tests de validación de la especificación de diseño."""

import pytest
from pydantic import ValidationError

from pcb_ai.spec import DesignSpec


def minimal_spec_dict() -> dict:
    return {
        "project": {"name": "demo", "revision": "A", "purpose": "placa de prueba"},
        "power_inputs": [
            {
                "name": "VBUS",
                "connector": "USB-C",
                "voltage_nominal_v": 5.0,
                "voltage_range": {"min_v": 4.5, "max_v": 5.5},
                "max_current_a": 1.5,
                "protection": ["ESD"],
            }
        ],
        "power_rails": [
            {
                "name": "3V3",
                "voltage_v": 3.3,
                "tolerance_pct": 3.0,
                "max_current_a": 0.5,
                "source": "regulador_3v3",
            }
        ],
        "interfaces": [{"name": "i2c0", "type": "i2c"}],
        "functional_blocks": [
            {"name": "regulador_3v3", "purpose": "LDO 5V a 3.3V"},
            {"name": "mcu", "purpose": "microcontrolador", "interfaces": ["i2c0"]},
        ],
        "constraints": {
            "board": {"max_width_mm": 60, "max_height_mm": 40, "layers": 2},
        },
        "critical_nets": [
            {"name": "VBUS", "net_class": "power_critical", "rules": "ancho >= 0.5mm"}
        ],
        "manufacturing": {
            "target_fab": "JLCPCB",
            "assembly": "manual",
            "min_trace_mm": 0.15,
            "min_clearance_mm": 0.15,
            "min_drill_mm": 0.3,
        },
        "verification": {"required_simulations": ["regulador_3v3"]},
    }


def test_valid_minimal_spec():
    spec = DesignSpec.model_validate(minimal_spec_dict())
    assert spec.project.name == "demo"
    assert spec.power_rails[0].source == "regulador_3v3"


def test_rail_source_must_exist():
    data = minimal_spec_dict()
    data["power_rails"][0]["source"] = "fuente_fantasma"
    with pytest.raises(ValidationError, match="fuente_fantasma"):
        DesignSpec.model_validate(data)


def test_block_interface_must_exist():
    data = minimal_spec_dict()
    data["functional_blocks"][1]["interfaces"] = ["spi_inexistente"]
    with pytest.raises(ValidationError, match="spi_inexistente"):
        DesignSpec.model_validate(data)


def test_required_simulation_must_reference_block():
    data = minimal_spec_dict()
    data["verification"]["required_simulations"] = ["bloque_fantasma"]
    with pytest.raises(ValidationError, match="bloque_fantasma"):
        DesignSpec.model_validate(data)


def test_typo_field_rejected():
    data = minimal_spec_dict()
    data["proyecto"] = {"name": "typo"}
    with pytest.raises(ValidationError):
        DesignSpec.model_validate(data)


def test_voltage_range_order():
    data = minimal_spec_dict()
    data["power_inputs"][0]["voltage_range"] = {"min_v": 5.5, "max_v": 4.5}
    with pytest.raises(ValidationError, match="min_v"):
        DesignSpec.model_validate(data)


def test_no_power_input_rejected():
    data = minimal_spec_dict()
    data["power_inputs"] = []
    with pytest.raises(ValidationError):
        DesignSpec.model_validate(data)


def test_invalid_layer_count_rejected():
    data = minimal_spec_dict()
    data["constraints"]["board"]["layers"] = 3
    with pytest.raises(ValidationError):
        DesignSpec.model_validate(data)
