"""Tests del modelo demo-vigia y del generador de esquemáticos.

Los tests del modelo son puros (sin KiCad). La emisión real se prueba en
test_emit_* solo si hay KiCad instalado (misma máquina del pipeline).
"""

from __future__ import annotations

import pytest

from pcb_ai import schematic
from pcb_ai.boards.demo_vigia import CONTRACT_NETS, build_model
from pcb_ai.schematic import EmitError, Part, _guard_before_emit, kicad_share_dir


@pytest.fixture()
def model():
    return build_model()


def test_model_is_internally_valid(model):
    assert model.validate() == []


def test_contract_nets_all_present(model):
    missing = CONTRACT_NETS - model.nets()
    assert not missing, f"nets del contrato ausentes: {sorted(missing)}"


def test_tvs_polarity_unidirectional(model):
    """SMF5.0A es unidireccional: K (pin 1) a VBUS_5V, A (pin 2) a GND.

    El símbolo es Device:D_Zener a propósito — Diode:SMF5V0A es bidireccional
    en la librería oficial y ocultaría la polaridad (ver docstring del board).
    """
    d2 = model.part("D2")
    assert d2.lib_id == "Device:D_Zener"
    assert d2.footprint == "Diode_SMD:D_SMF"
    assert d2.pins["1"] == "VBUS_5V"
    assert d2.pins["2"] == "GND"


def test_led_polarity_active_high(model):
    d1 = model.part("D1")
    assert d1.pins["1"] == "GND"  # K
    assert d1.pins["2"] == "LED_A"  # A, hacia la resistencia serie


def test_swd_header_order_per_spec(model):
    j2 = model.part("J2")
    assert [j2.pins[str(n)] for n in range(1, 6)] == [
        "+3V3",
        "SWDIO",
        "SWCLK",
        "NRST",
        "GND",
    ]


def test_ldo_enable_tied_to_vin(model):
    u2 = model.part("U2")
    assert u2.pins["3"] == u2.pins["1"] == "VBUS_5V"


def test_lm75b_address_0x48(model):
    u3 = model.part("U3")
    assert u3.lib_id == "Sensor_Temperature:LM75C"
    assert u3.value == "LM75BD"
    assert u3.pins["5"] == u3.pins["6"] == u3.pins["7"] == "GND"


def test_mcu_swd_and_i2c_pins_match_datasheet(model):
    """DS12991 Table 12: SWDIO=18, SWCLK=19, I2C1 SDA=PB7(1), SCL=PB6(20)."""
    u1 = model.part("U1")
    assert u1.pins["18"] == "SWDIO"
    assert u1.pins["19"] == "SWCLK"
    assert u1.pins["1"] == "I2C_SDA"
    assert u1.pins["20"] == "I2C_SCL"


def test_every_fabricated_part_has_footprint(model):
    sin_footprint = [
        p.reference
        for p in model.parts
        if p.footprint is None and not p.reference.startswith("#")
    ]
    assert sin_footprint == [], f"componentes sin footprint: {sin_footprint}"


def test_validate_rejects_duplicate_refs(model):
    dup = model.parts + (model.parts[0],)
    bad = schematic.BoardModel(name="x", revision="A", parts=dup)
    assert any("duplicada" in p for p in bad.validate())


def test_validate_rejects_off_grid_position():
    part = Part(
        reference="R1",
        lib_id="Device:R",
        value="1k",
        position=(10.0, 10.16),  # 10.0 no es múltiplo de 1.27
    )
    bad = schematic.BoardModel(name="x", revision="A", parts=(part,))
    assert any("grid" in p for p in bad.validate())


# ---------------- hash-guard ----------------


@pytest.fixture()
def isolated_registry(tmp_path, monkeypatch):
    registry = tmp_path / "emitted.sha256"
    monkeypatch.setattr(schematic, "HASH_REGISTRY", registry)
    return registry


def test_guard_rejects_unregistered_existing_file(tmp_path, isolated_registry):
    target = tmp_path / "a.kicad_sch"
    target.write_text("manual", encoding="utf-8")
    with pytest.raises(EmitError, match="sin registro"):
        _guard_before_emit([target], force=False)


def test_guard_rejects_externally_modified_file(tmp_path, isolated_registry):
    target = tmp_path / "a.kicad_sch"
    target.write_text("v1", encoding="utf-8")
    schematic._save_registry({schematic._rel_key(target): schematic._sha256(target)})
    target.write_text("editado a mano", encoding="utf-8")
    with pytest.raises(EmitError, match="hash-guard"):
        _guard_before_emit([target], force=False)


def test_guard_accepts_unmodified_file_and_force(tmp_path, isolated_registry):
    target = tmp_path / "a.kicad_sch"
    target.write_text("v1", encoding="utf-8")
    schematic._save_registry({schematic._rel_key(target): schematic._sha256(target)})
    _guard_before_emit([target], force=False)  # no debe lanzar
    target.write_text("editado", encoding="utf-8")
    _guard_before_emit([target], force=True)  # force ignora el guard


def test_guard_rejects_kicad_lockfile(tmp_path, isolated_registry):
    target = tmp_path / "a.kicad_sch"
    (tmp_path / "~a.kicad_sch.lck").write_text("", encoding="utf-8")
    with pytest.raises(EmitError, match="lockfile"):
        _guard_before_emit([target], force=False)


# ---------------- emisión real (requiere KiCad instalado) ----------------


@pytest.mark.skipif(kicad_share_dir() is None, reason="KiCad no instalado")
def test_emit_creates_parseable_project(tmp_path, isolated_registry, model):
    result = schematic.emit(model, tmp_path / "out")
    assert result.schematic.exists()
    assert result.project.exists()
    text = result.schematic.read_text(encoding="utf-8")
    for net in sorted(CONTRACT_NETS):
        assert f'"{net}"' in text, f"label {net} no está en el archivo emitido"
    # re-emisión sin ediciones externas debe pasar el guard
    schematic.emit(model, tmp_path / "out")
