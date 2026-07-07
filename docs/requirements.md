# Requisitos — demo-vigia rev A

Fuente autoritativa: `spec/design_spec.yaml` (este documento la narra, no la sustituye).

## Objetivo

Placa demostradora end-to-end del pipeline agéntico `pcb-ai`: probar que el sistema
puede ir de una spec validada a un paquete de fabricación con validación determinista
en cada etapa (ERC, simulación, DRC, red team).

## Requisitos funcionales

| ID | Requisito | Verificación |
|---|---|---|
| RF-1 | Alimentación por USB-C (solo power, sink 5 V) | Continuidad VBUS; CC1/CC2 con pull-down 5.1 kΩ |
| RF-2 | Rail regulado +3V3, hasta 300 mA | Simulación del bloque regulador + medición en bring-up |
| RF-3 | Protección de entrada: sobrecorriente (PPTC 500 mA) y transitorios (TVS) | Presencia en netlist (verify-spec) + revisión red team |
| RF-4 | MCU ARM Cortex-M moderno programable por SWD sin bootloader | Bring-up SWD |
| RF-5 | LED de usuario controlado por GPIO | Firmware de prueba |
| RF-6 | Botón de usuario con pull-up y filtro de rebote | Firmware de prueba |
| RF-7 | Sensor de temperatura I2C legible por el MCU | Lectura I2C en bring-up |

## Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-1 | Placa ≤ 50×50 mm, 2 capas, fabricable en JLCPCB (reglas en la spec) |
| RNF-2 | Soldable a mano o ensamblado mixto: sin BGA/QFN sin pines accesibles |
| RNF-3 | Todos los componentes con símbolo/footprint en librerías oficiales KiCad 10 |
| RNF-4 | Componentes en producción activa con stock verificable (LCSC/JLCPCB) |
| RNF-5 | Test points o pads medibles en VBUS_5V y +3V3 |

## Criterios de aceptación del demostrador (Definition of Done por fase)

1. Spec validada por schema (hecho: `pcb-ai spec validate` verde).
2. Selección de componentes con evidencia primaria de datasheet (`docs/component_selection.md`).
3. Proyecto KiCad real generado; ERC terminal VERDE citando reporte JSON.
4. Simulación ngspice del bloque `regulador_3v3` con resultados documentados.
5. PCB con placement scriptado y DRC terminal VERDE citando reporte JSON.
6. Revisión red team independiente documentada (BLOCKER → INFORMATIONAL).
7. `manufacturing/rev_A/` con Gerbers, drill, BOM y pick-and-place no vacíos.
