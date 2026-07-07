# Constraints de PCB — demo-vigia rev A

Entradas: `spec/design_spec.yaml` (placa 50×50 mm, 2 capas, JLCPCB),
`bom/component_candidates.csv` (packages), `docs/electrical_architecture.md` (nets).
Este documento gobierna placement y routing (fases 7-10); las reglas duras se
materializan en el `.kicad_pro`/board setup y las verifica el DRC.

## Reglas de fabricación (JLCPCB 2 capas, de la spec — conservadoras)

| Regla | Valor |
|---|---|
| Traza / clearance mínimos | 0.2 mm / 0.2 mm |
| Drill mínimo | 0.3 mm (vía 0.6/0.3 mm estándar) |
| Stackup | FR-4 1.6 mm, cobre 1 oz, HASL |
| Montaje | Una cara (top) — supuesto Q-4 de open_questions |

## Clases de red (a configurar en board setup)

| Clase | Nets | Ancho | Clearance | Nota |
|---|---|---|---|---|
| Power_VBUS | VBUS_IN, VBUS_5V | ≥ 0.5 mm | 0.2 mm | regla de la spec (net crítica) |
| Power_3V3 | +3V3 | ≥ 0.4 mm | 0.2 mm | regla de la spec (net crítica) |
| Default | resto (señales) | 0.25 mm | 0.2 mm | margen sobre el mínimo de fab |

GND no lleva clase de ancho: se sirve por planos/pours en ambas caras con costura
de vías.

## Estrategia de placement (por bloques, flujo de potencia de izquierda a derecha)

1. **USB-C en el borde izquierdo** (constraint mecánico de la spec), overhang según
   footprint HRO. Pull-downs CC junto al conector.
2. **Cadena de protección en línea recta y corta**: conector → PPTC (1812) → nodo
   TVS → entrada LDO. El TVS con retorno directo a GND (vía propia al plano, loop
   mínimo — es la ruta del transitorio).
3. **LDO + sus 1 µF**: condensadores de entrada y salida a < 2 mm de los pines VIN/VOUT
   (exigencia de estabilidad del datasheet AP2112).
4. **MCU al centro**: 100 nF de desacoplo adyacente al par VDD/VSS (pines 16/15,
   mismo lado del package), bulk 4.7 µF cerca; condensador de NRST junto al pin 4.
5. **Sensor LM75BD alejado del LDO** (≥ 10 mm) y con posibilidad de ranura de aislamiento
   térmico si se decide en Q-3; pull-ups I2C entre MCU y sensor.
6. **UI (LED, botón) y header SWD en el borde derecho/inferior**: accesibles con la
   placa montada.
7. **Taladros de montaje M2.5 en las 4 esquinas** (spec), keep-out de cobre alrededor.
8. **Test points TP_VBUS y TP_3V3** en zona despejada, accesibles con sonda.

## Estrategia de routing

- **Manual (crítico):** camino de potencia completo (VBUS_IN → PPTC → TVS → LDO →
  +3V3) con los anchos de clase; retornos de los condensadores de desacoplo.
- **Automatizable (no crítico):** I2C_SDA/SCL, SWDIO/SWCLK/NRST, LED_CTRL, BTN_SENSE —
  señales lentas (≤ 100 kHz I2C, SWD de programación) sin requisitos de impedancia.
  FreeRouting 2.2.4 SOLO si su smoke test DSN pasa (deuda §5 de architecture.md);
  si no, también manual/scriptado.
- **GND:** pour en ambas caras, costura de vías perimetral y bajo el MCU; ningún
  retorno de señal debe cruzar cortes del plano.
- I2C: pistas cortas y juntas; no rodear la placa.

## Térmica

- LDO: disipación peor caso continua 0.66 W (300 mA × 2.2 V) excede lo razonable
  para SOT-25 sin cobre (θJA ~250 °C/W) — PERO el presupuesto real es < 50 mA
  (0.11 W → ΔT ≈ 28 °C, aceptable). Regla: pour de cobre en el pad de VOUT/GND del
  LDO como disipador; el red team valida el peor caso.
- Sensor: la exactitud del LM75 mide la placa, no el aire — documentado en Q-3.

## Criterio de salida de fase (Definition of Done)

1. Placement scriptado reproducible (vía `pcb_backend`, SWIG aislado — ADR-0001 H5).
2. DRC terminal VERDE con reporte JSON citado (mismos estados que ERC: VERDE /
   ESTANCADO / AGOTADO, sin exclusions automáticas).
3. Las nets de clase Power con su ancho verificable en el DRC (regla custom o
   inspección documentada).
