# Arquitectura eléctrica — demo-vigia rev A

Derivada de `spec/design_spec.yaml`. Los MPN exactos viven en
`docs/component_selection.md` y `bom/component_candidates.csv` (evidencia primaria).

## Diagrama de bloques

```text
USB-C (power-only)                                        header SWD 1x5
  VBUS ──► PPTC 500mA ──► TVS ──► LDO 3.3V ──► +3V3 ──┬──► MCU ◄────────┘
  CC1/CC2 ── 5.1k ── GND        (entrada/salida        │    │ │ │
  GND ─────────────────────      según datasheet)      │    │ │ └─ GPIO ── botón ── GND
                                                       │    │ │        (pull-up + RC)
                                                       │    │ └─ GPIO ── R serie ── LED ── GND
                                                       │    └─ I2C (SDA/SCL, pull-ups 4.7k)
                                                       │         │
                                                       └────► sensor de temperatura I2C
```

## Presupuesto de potencia (peor caso)

| Consumidor | Corriente estimada | Base |
|---|---|---|
| MCU (run, periféricos activos) | ≤ 10 mA | datasheet del MCU elegido (ver component_selection) |
| Sensor I2C | ≤ 1 mA | datasheet |
| LED usuario | ~2 mA | fijado por R serie |
| Pull-ups I2C (2 × 4.7 kΩ activos) | ~1.4 mA | ley de Ohm a 3.3 V |
| Margen ×3 + reserva expansión | — | — |
| **Total presupuestado** | **< 50 mA** ≪ 300 mA del rail | holgura amplia para el LDO |

Disipación del LDO en peor caso: (5.5 − 3.3) V × 0.05 A ≈ 0.11 W — trivial para
cualquier package SOT-23-5/SOT-223. A los 300 mA de límite del rail serían 0.66 W:
se verifica contra el θJA del package elegido en la revisión red team.

## Decisiones eléctricas y su porqué

1. **USB-C solo alimentación.** CC1 y CC2 con pull-down de 5.1 kΩ independientes
   (nunca compartida: el cargador debe ver Rd en cada CC para anunciar sink).
   Sin USB data → sin ESD array en D±; D+/D− quedan sin conectar.
2. **Orden de protección: conector → PPTC → TVS → LDO.** El PPTC limita la corriente
   de falla aguas abajo; el TVS tras el PPTC recorta transitorios y, ante sobretensión
   sostenida, su conducción dispara el PPTC (crowbar suave).
3. **LDO, no buck.** Carga < 50 mA típica y ΔV pequeño: la simplicidad y el ruido bajo
   ganan a la eficiencia. Condensadores de entrada/salida exactamente los del datasheet
   (hallazgo típico de red team: LDO inestable por ESR/valor incorrecto).
4. **NRST y BOOT según datasheet del MCU** (condensador en NRST; estrategia BOOT
   documentada en component_selection — en STM32G0 el boot de fábrica se controla por
   option bits, verificar antes de fijar hardware).
5. **I2C a 100 kHz con pull-ups 4.7 kΩ** — bus corto en placa, capacitancia baja;
   valor estándar conservador.
6. **Botón con pull-up externo + RC** en lugar de depender del pull-up interno del
   MCU: comportamiento definido aunque el firmware no configure el pin.
7. **Desacoplo:** 100 nF por pin de VDD del MCU + bulk local (valor según datasheet),
   100 nF en el sensor. Colocación adyacente al pin (constraint de placement).

## Mapa spec → nets esperadas en el esquemático

| Elemento de la spec | Nets en KiCad |
|---|---|
| rail VBUS_5V | `VBUS_5V` (tramo protegido: `VBUS_IN` antes del PPTC) |
| rail +3V3 | `+3V3` |
| i2c_bus | `I2C_SDA`, `I2C_SCL` |
| swd_debug | `SWDIO`, `SWCLK`, `NRST` |
| gpio_led | `LED_CTRL` |
| gpio_boton | `BTN_SENSE` |
| referencia | `GND` |

Esta tabla es el contrato que `pcb-ai verify-spec` comprueba contra el netlist.
