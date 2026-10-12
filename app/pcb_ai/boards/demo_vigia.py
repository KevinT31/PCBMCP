"""demo-vigia rev A — modelo de esquemático.

Fuentes del mapa pin→net (regla: ninguna conexión sin fuente primaria):
- Pinouts: knowledge/datasheet_facts/{stm32g030f6p6,ap2112k-3.3trg1,lm75bd,type-c-31-m-12}.md
- Nets del contrato: docs/electrical_architecture.md ("Mapa spec → nets esperadas")
- MPN/footprints: bom/component_candidates.csv
- Números de pin cotejados contra las librerías KiCad 10.0.3 instaladas
  (scripts/dump_symbol_pins.py, 2026-07-07).

Desviación registrada respecto a la BOM: el símbolo `Diode:SMF5V0A` de la librería
oficial extiende `SM6T6V8A` (TVS bidireccional, pines A1/A2) y ocultaría la polaridad
de la pieza real (Littelfuse SMF5.0A, unidireccional). Se usa `Device:D_Zener`
(1=K, 2=A), que casa 1:1 con el footprint `Diode_SMD:D_SMF` (pad 1 = cátodo).
"""

from __future__ import annotations

from pcb_ai.schematic import BoardModel, Note, Part

# Contrato de nets que verify-spec comprobará (docs/electrical_architecture.md).
CONTRACT_NETS = frozenset(
    {
        "VBUS_IN",
        "VBUS_5V",
        "+3V3",
        "GND",
        "I2C_SDA",
        "I2C_SCL",
        "SWDIO",
        "SWCLK",
        "NRST",
        "LED_CTRL",
        "BTN_SENSE",
    }
)

_R_0603 = "Resistor_SMD:R_0603_1608Metric"
_C_0603 = "Capacitor_SMD:C_0603_1608Metric"


def build_model() -> BoardModel:
    parts: list[Part] = []

    # ---- Bloque: entrada USB-C solo-alimentación + protección ----
    parts.append(
        Part(
            reference="J1",
            lib_id="Connector:USB_C_Receptacle_USB2.0_16P",
            value="TYPE-C-31-M-12",
            position=(38.10, 88.90),
            footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
            # VBUS A4/A9/B4/B9 y GND A1/A12/B1/B12 están apilados en el símbolo:
            # un label en el pin visible conecta el stack completo.
            pins={
                "A4": "VBUS_IN",
                "A1": "GND",
                "SH": "GND",
                "A5": "USB_CC1",
                "B5": "USB_CC2",
            },
            # Power-only: D+/D-/SBU sin conectar (electrical_architecture.md #1)
            nc_pins=("A6", "A7", "A8", "B6", "B7", "B8"),
            properties={"MPN": "TYPE-C-31-M-12", "LCSC": "C165948"},
        )
    )
    # Rd = 5.1k por pin CC, nunca compartida (USB Type-C sink)
    parts.append(
        Part(
            reference="R5",
            lib_id="Device:R",
            value="5.1k",
            position=(66.04, 116.84),
            footprint=_R_0603,
            pins={"1": "USB_CC1", "2": "GND"},
            properties={"MPN": "0603WAF5101T5E", "LCSC": "C23186"},
        )
    )
    parts.append(
        Part(
            reference="R6",
            lib_id="Device:R",
            value="5.1k",
            position=(76.20, 116.84),
            footprint=_R_0603,
            pins={"1": "USB_CC2", "2": "GND"},
            properties={"MPN": "0603WAF5101T5E", "LCSC": "C23186"},
        )
    )
    # Orden de protección: conector → PPTC → TVS (electrical_architecture.md #2)
    parts.append(
        Part(
            reference="F1",
            lib_id="Device:Polyfuse_Small",
            value="500mA",
            position=(81.28, 45.72),
            rotation=90.0,
            footprint="Fuse:Fuse_1812_4532Metric_Pad1.30x3.40mm_HandSolder",
            pins={"1": "VBUS_IN", "2": "VBUS_5V"},
            properties={"MPN": "MF-MSMF050-2", "LCSC": "C17313"},
        )
    )
    parts.append(
        Part(
            reference="D2",
            lib_id="Device:D_Zener",  # ver desviación documentada en el docstring
            value="SMF5.0A",
            position=(96.52, 63.50),
            rotation=90.0,
            footprint="Diode_SMD:D_SMF",
            pins={"1": "VBUS_5V", "2": "GND"},  # 1=K a VBUS, 2=A a GND (unidireccional)
            properties={"MPN": "SMF5.0A", "LCSC": "C151296"},
        )
    )

    # ---- Bloque: regulador 3.3 V ----
    parts.append(
        Part(
            reference="U2",
            lib_id="Regulator_Linear:AP2112K-3.3",
            value="AP2112K-3.3",
            position=(127.00, 48.26),
            footprint="Package_TO_SOT_SMD:SOT-23-5",
            # EN a VIN para encendido permanente (AP2112 DS p.8: pull-down interno 3 MΩ)
            pins={"1": "VBUS_5V", "2": "GND", "3": "VBUS_5V", "5": "+3V3"},
            nc_pins=("4",),
            properties={"MPN": "AP2112K-3.3TRG1", "LCSC": "C51118"},
        )
    )
    # CIN = COUT = 1 µF cerámico X5R/X7R, exigidos por AP2112 DS p.2 Nota 4
    parts.append(
        Part(
            reference="C1",
            lib_id="Device:C",
            value="1uF",
            position=(110.49, 55.88),
            footprint=_C_0603,
            pins={"1": "VBUS_5V", "2": "GND"},
            properties={"MPN": "CL10A105KB8NNNC", "LCSC": "C15849"},
        )
    )
    parts.append(
        Part(
            reference="C2",
            lib_id="Device:C",
            value="1uF",
            position=(147.32, 55.88),
            footprint=_C_0603,
            pins={"1": "+3V3", "2": "GND"},
            properties={"MPN": "CL10A105KB8NNNC", "LCSC": "C15849"},
        )
    )
    # Rails medibles (constraint de la spec)
    parts.append(
        Part(
            reference="TP1",
            lib_id="Connector:TestPoint",
            value="VBUS_5V",
            position=(99.06, 38.10),
            footprint="TestPoint:TestPoint_Pad_1.5x1.5mm",
            pins={"1": "VBUS_5V"},
        )
    )
    parts.append(
        Part(
            reference="TP2",
            lib_id="Connector:TestPoint",
            value="+3V3",
            position=(157.48, 38.10),
            footprint="TestPoint:TestPoint_Pad_1.5x1.5mm",
            pins={"1": "+3V3"},
        )
    )

    # ---- Bloque: MCU STM32G030F6P6 (TSSOP-20, DS12991 Table 12) ----
    parts.append(
        Part(
            reference="U1",
            lib_id="MCU_ST_STM32G0:STM32G030F6Px",
            value="STM32G030F6P6",
            position=(198.12, 78.74),
            footprint="Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
            pins={
                "4": "+3V3",  # VDD/VDDA
                "5": "GND",  # VSS/VSSA
                "6": "NRST",
                "1": "I2C_SDA",  # PB7 = I2C1_SDA (bootloader I2C usa PB6/PB7)
                "20": "I2C_SCL",  # PB6 = I2C1_SCL
                "18": "SWDIO",  # PA13
                "19": "SWCLK",  # PA14-BOOT0; sin strap: boot por option bytes
                "7": "BTN_SENSE",  # PA0
                "12": "LED_CTRL",  # PA5
            },
            # Q-5 abierta (docs/open_questions.md): pines libres quedan NC en rev A
            nc_pins=("2", "3", "8", "9", "10", "11", "13", "14", "15", "16", "17"),
            properties={"MPN": "STM32G030F6P6", "LCSC": "C724040"},
        )
    )
    # Desacoplo DS12991 Fig. 9: 100 nF + 4.7 µF junto a VDD/VDDA
    parts.append(
        Part(
            reference="C3",
            lib_id="Device:C",
            value="100nF",
            position=(172.72, 116.84),
            footprint=_C_0603,
            pins={"1": "+3V3", "2": "GND"},
            properties={"MPN": "CL10B104KB8NNNC", "LCSC": "C1591"},
        )
    )
    parts.append(
        Part(
            reference="C4",
            lib_id="Device:C",
            value="4.7uF",
            position=(185.42, 116.84),
            footprint="Capacitor_SMD:C_0805_2012Metric",
            pins={"1": "+3V3", "2": "GND"},
            properties={"MPN": "CL21A475KAQNNNE", "LCSC": "C1779"},
        )
    )
    # NRST: 0.1 µF a GND, sin R externa (DS12991 Fig. 19, pull-up interno 25-55k)
    parts.append(
        Part(
            reference="C5",
            lib_id="Device:C",
            value="100nF",
            position=(160.02, 96.52),
            footprint=_C_0603,
            pins={"1": "NRST", "2": "GND"},
            properties={"MPN": "CL10B104KB8NNNC", "LCSC": "C1591"},
        )
    )

    # ---- Bloque: header SWD (orden de la spec: 3V3 SWDIO SWCLK NRST GND) ----
    parts.append(
        Part(
            reference="J2",
            lib_id="Connector_Generic:Conn_01x05",
            value="SWD",
            position=(259.08, 48.26),
            footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
            pins={"1": "+3V3", "2": "SWDIO", "3": "SWCLK", "4": "NRST", "5": "GND"},
        )
    )

    # ---- Bloque: sensor de temperatura I2C (LM75BD, dirección 0x48) ----
    parts.append(
        Part(
            reference="U3",
            # LM75B es alias de LM75C en KiCad 10. El generador expande el alias
            # y KiCad marca la copia embebida como lib_symbol_mismatch.
            lib_id="Sensor_Temperature:LM75C",
            value="LM75BD",
            position=(45.72, 165.10),
            footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
            # A2..A0 a GND → 0x48; SDA/SCL/Ax sin bias interno: no flotar (DS §7.3)
            pins={
                "1": "I2C_SDA",
                "2": "I2C_SCL",
                "4": "GND",
                "5": "GND",  # A2
                "6": "GND",  # A1
                "7": "GND",  # A0
                "8": "+3V3",
            },
            nc_pins=("3",),  # O.S. sin uso en rev A (datasheet_facts/lm75bd.md)
            properties={"MPN": "LM75BD,118", "LCSC": "C34565"},
        )
    )
    parts.append(
        Part(
            reference="C6",
            lib_id="Device:C",
            value="100nF",
            position=(66.04, 152.40),
            footprint=_C_0603,
            pins={"1": "+3V3", "2": "GND"},
            properties={"MPN": "CL10B104KB8NNNC", "LCSC": "C1591"},
        )
    )
    # Pull-ups I2C 4.7k a +3V3 (100 kHz, bus corto — electrical_architecture.md #5)
    parts.append(
        Part(
            reference="R1",
            lib_id="Device:R",
            value="4.7k",
            position=(83.82, 160.02),
            footprint=_R_0603,
            pins={"1": "+3V3", "2": "I2C_SDA"},
            properties={"MPN": "0603WAF4701T5E", "LCSC": "C23162"},
        )
    )
    parts.append(
        Part(
            reference="R2",
            lib_id="Device:R",
            value="4.7k",
            position=(93.98, 160.02),
            footprint=_R_0603,
            pins={"1": "+3V3", "2": "I2C_SCL"},
            properties={"MPN": "0603WAF4701T5E", "LCSC": "C23162"},
        )
    )

    # ---- Bloque: LED de usuario (activo alto, ~2 mA con 680R) ----
    parts.append(
        Part(
            reference="R3",
            lib_id="Device:R",
            value="680R",
            position=(127.00, 165.10),
            rotation=90.0,
            footprint=_R_0603,
            pins={"1": "LED_CTRL", "2": "LED_A"},
            properties={"MPN": "0603WAF6800T5E", "LCSC": "C23228"},
        )
    )
    parts.append(
        Part(
            reference="D1",
            lib_id="Device:LED",
            value="KT-0603R",
            position=(147.32, 165.10),
            footprint="LED_SMD:LED_0603_1608Metric",
            pins={"2": "LED_A", "1": "GND"},  # 2=A desde la resistencia, 1=K a GND
            properties={"MPN": "KT-0603R", "LCSC": "C2286"},
        )
    )

    # ---- Bloque: botón de usuario (pull-up 10k + RC 100 nF, tau = 1 ms) ----
    parts.append(
        Part(
            reference="R4",
            lib_id="Device:R",
            value="10k",
            position=(198.12, 152.40),
            footprint=_R_0603,
            pins={"1": "+3V3", "2": "BTN_SENSE"},
            properties={"MPN": "0603WAF1002T5E", "LCSC": "C25804"},
        )
    )
    parts.append(
        Part(
            reference="C7",
            lib_id="Device:C",
            value="100nF",
            position=(198.12, 172.72),
            footprint=_C_0603,
            pins={"1": "BTN_SENSE", "2": "GND"},
            properties={"MPN": "CL10B104KB8NNNC", "LCSC": "C1591"},
        )
    )
    parts.append(
        Part(
            reference="SW1",
            lib_id="Switch:SW_Push",
            value="TS-1187A-B-A-B",
            position=(218.44, 172.72),
            footprint="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A",
            pins={"1": "BTN_SENSE", "2": "GND"},
            properties={"MPN": "TS-1187A-B-A-B", "LCSC": "C318884"},
        )
    )

    # ---- PWR_FLAG: nets alimentadas solo por pines passive (conector/PPTC) ----
    # +3V3 no lo necesita: VOUT del AP2112K es power_out.
    for i, (net, pos) in enumerate(
        [("VBUS_IN", (60.96, 40.64)), ("VBUS_5V", (104.14, 40.64)), ("GND", (256.54, 165.10))],
        start=1,
    ):
        parts.append(
            Part(
                reference=f"#FLG{i}",
                lib_id="power:PWR_FLAG",
                value="PWR_FLAG",
                position=pos,
                pins={"1": net},
            )
        )

    # ---- Mecánica: 4 taladros M2.5 (constraint de la spec) ----
    for i, x in enumerate((251.46, 259.08, 266.70, 274.32), start=1):
        parts.append(
            Part(
                reference=f"H{i}",
                lib_id="Mechanical:MountingHole",
                value="M2.5",
                position=(x, 190.50),
                footprint="MountingHole:MountingHole_2.7mm_M2.5",
            )
        )

    notes = (
        Note("demo-vigia rev A — generado por pcb-ai (no editar a mano: ver architecture.md)", (20.32, 20.32), size=2.5),
        Note("ENTRADA USB-C + PROTECCION", (20.32, 30.48)),
        Note("LDO 5V->3.3V", (115.57, 30.48)),
        Note("MCU STM32G030F6P6", (170.18, 48.26)),
        Note("SWD", (250.19, 30.48)),
        Note("SENSOR TEMP I2C 0x48", (20.32, 140.97)),
        Note("LED USUARIO", (120.65, 149.86)),
        Note("BOTON USUARIO", (190.50, 140.97)),
    )

    return BoardModel(name="demo-vigia", revision="A", parts=tuple(parts), notes=notes)
