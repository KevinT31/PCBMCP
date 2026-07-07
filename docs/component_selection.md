# Selección de componentes — demo-vigia Rev A

Fecha: 2026-07-07. Matriz completa en `bom/component_candidates.csv`. Hechos con página en
`knowledge/datasheet_facts/`. Estados: **V**ERIFIED / **I**NFERRED / **U**NVERIFIED.

Notas de método:
- st.com, nxp.com directo, littelfuse.com y krhro.com bloquean descargas desde esta red; donde se
  indica "mirror" se leyó una copia íntegra del documento oficial (mismo número de documento y
  revisión declarada) y se cita la URL oficial del fabricante. Para st.com (DS12991 Rev 4, LD1117),
  littelfuse.com (SMF Rev 05/15/20) y krhro.com (plano TYPE-C-31-M-12 Rev A) se leyeron además
  **capturas de Wayback Machine de la URL oficial exacta**, lo que eleva esos hechos a VERIFIED.
- Stock/precio: API pública de LCSC (`wmsc.lcsc.com`), consultada 2026-07-07. Los códigos se
  validaron comprobando que el `productModel` devuelto coincide con el MPN.
- Símbolos/footprints: verificados por existencia (y pin a pin en los activos) en las librerías
  oficiales instaladas de KiCad 10.0.3 (`%LOCALAPPDATA%\Programs\KiCad\10.0\share\kicad\`).

---

## 1. MCU — elegido: STM32G030F6P6 (TSSOP-20) [V]

Evidencia: DS12991 (https://www.st.com/resource/en/datasheet/stm32g030f6.pdf; leído en dos
revisiones independientes — Rev 3 vía mirror y Rev 4 vía captura Wayback de st.com, hechos
idénticos; Rev vigente 6, "product in full production"), RM0454 Rev 2, AN5096.

| Criterio | STM32G030F6P6 | STM32C031C6T6 |
|---|---|---|
| Producción | Activa (DS Rev 6 jun-2025 "full production") [V] | Activa [I] |
| Precio LCSC q1 | **0.95 USD** (C724040) / 0.86 TR (C529330) [V] | 1.41 USD (C5456218) [V] |
| Stock LCSC | 3 394 + 6 046 (TR) [V] | 1 252 [V] |
| Package | TSSOP-20 0.65 mm, 20 pines — menos pines que rutear en 2 capas | LQFP-48 0.5 mm, 48 pines |
| Pines requeridos | SWD (PA13/PA14) + I2C1 (PB6/PB7) + 8 GPIO libres (PA0..PA7) — suficiente [V] | Sobrado |
| BOOT/NRST | Idéntico en ambos (familia G0/C0): boot por option bytes, NRST con 0.1 µF | Igual |
| KiCad oficial | `MCU_ST_STM32G0:STM32G030F6Px` + `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` [V] | `MCU_ST_STM32C0:STM32C031C6Tx` + `Package_QFP:LQFP-48_7x7mm_P0.5mm` [V] |

Decisión: **STM32G030F6P6** — más barato, más stock, package más pequeño para placa de 50×50 mm y
pitch 0.65 mm más cómodo a mano que 0.5 mm. El C031C6T6 queda como alternativa verificada.

### Hechos críticos (detalle en knowledge/datasheet_facts/stm32g030f6p6.md)
- Alimentación: pin 4 = VDD/VDDA, pin 5 = VSS/VSSA. Desacoplo **1×100 nF + 1×4.7 µF** cerámicos
  pegados al pin (Fig. 9, p.39) [V].
- NRST (pin 6): pull-up interno 25–55 kΩ; **0.1 µF a GND** cerca del chip (Fig. 19, p.66); sin
  resistencia externa [V].
- BOOT: de fábrica el boot se controla por option bytes (AN5096 p.27) y el *empty check* manda un
  chip virgen al bootloader (RM0454 p.47/50) → **sin strap BOOT0**; PA14 queda como SWCLK [V].
- SWD: SWDIO = PA13 (pin 18), SWCLK = PA14 (pin 19), AF por defecto tras reset [V].
- I2C1: **SCL = PB6 (pin 20), SDA = PB7 (pin 1)** (pines bonded; los hermanos PB3-PB5/PB8 quedan en
  analógico por defecto y no interfieren) [V].

## 2. LDO 5 V→3.3 V — elegido: AP2112K-3.3TRG1 (SOT-25) [V]

Evidencia: DS39724 Rev 2-2, https://www.diodes.com/assets/Datasheets/AP2112.pdf (leído íntegro).

- 600 mA min; **dropout 125 mV typ / 200 mV max @300 mA** (p.8) — margen holgado con 4.5 V min [V].
- **CIN = COUT = 1.0 µF cerámico X7R/X5R exactos según datasheet** (p.2, Nota 4) — estable con
  cerámica [V]. Abs. max entrada 6.5 V; operación 2.5–6.0 V (p.3) [V]. EN a VIN (VIH ≥ 1.5 V) [V].
- LCSC C51118 (Diodes genuino): 34 505 uds, 0.16 USD q5 [V].
- KiCad: `Regulator_Linear:AP2112K-3.3` (pines cotejados) + `Package_TO_SOT_SMD:SOT-23-5` [V].
- Rechazados: **LD1117S33TR** — datasheet ST leído (https://www.st.com/resource/en/datasheet/ld1117.pdf
  p.1, vía Wayback): "Low dropout voltage (1 V typ.)" y **"10 µF minimum capacitor is needed for
  stability"** — frente a 1 µF cerámico del AP2112; además IQ mucho mayor [V].
  **ME6211C33M5G** — símbolo KiCad existe, pero sin datasheet de fuente primaria accesible (solo
  copia LCSC) → queda de alternativa [U]. AMS1117 prohibido por spec.
- Riesgo documentado: el AP2112 en SOT89-5 tiene dos variantes (R5/R5A) con **pinout distinto**;
  irrelevante aquí porque se fija SOT-25, pero no sustituir package sin revisar (DS p.1).

## 3. Sensor temperatura I2C — elegido: LM75BD,118 (NXP, SO8) [V]

Evidencia: DS LM75B Rev 6.1, https://www.nxp.com/docs/en/data-sheet/LM75B.pdf (leído íntegro).

- SO8 soldable a mano; VCC 2.8–5.5 V [V]; LCSC C34565: 3 115 uds, 0.64 USD q5 [V].
- **Dirección I2C = 1001·A2·A1·A0 → 0x48 con A2..A0 a GND**; configurable hasta 8 direcciones;
  pines de dirección y SDA/SCL sin bias interno (no dejar flotantes) (p.7) [V].
- **Registro Temp: puntero 0x00 (por defecto al power-up), lectura de 2 bytes, 11 bits en
  complemento a dos, 0.125 °C/LSB; descartar la primera lectura** (p.5/8/9) [V].
- KiCad: `Sensor_Temperature:LM75B` (pines cotejados) + `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` [V].
- Riesgo: TI vende otro "LM75B" — fijar fabricante NXP en el BOM.
- Rechazados: **TMP102** (solo SOT563 1.6×1.6 mm — soldadura manual difícil) [I];
  **STTS22H** (UDFN-6 con pad expuesto, prohibido por spec, y **sin símbolo KiCad oficial** —
  ausencia verificada en las librerías locales) [V].

## 4. USB-C power-only — TYPE-C-31-M-12 (HRO / Korean Hroparts) [V]

- **Plano del fabricante leído** (HRO Electronics, Rev A, 2015.5.13; captura Wayback de
  http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf, la misma URL que cita el footprint
  oficial de KiCad). Hechos del plano [V]:
  - Tabla de pines: A1/A12/B1/B12 = GND; A4/A9/B4/B9 = VBUS; **A5 = CC1, B5 = CC2**; A6/B6 = DP;
    A7/B7 = DN; A8/B8 = SBU (16 contactos, variante USB 2.0).
  - Corriente nominal: **3 A min en VBUS**, 0.25 A min resto; resistencia de contacto ≤ 40 mΩ;
    aislamiento ≥ 100 MΩ; rigidez 250 V AC; 10 000 ciclos; −55 a +85 °C; carcasa inox 0.30 mm.
  - Incluye "Recommended PCB layout" (16 pads 0.25×... paso fino + 4 anclajes) — coherente con el
    footprint oficial de KiCad.
- Footprint oficial KiCad `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` **diseñado para este
  MPN exacto** [V, en disco]. Símbolo `Connector:USB_C_Receptacle_USB2.0_16P` [V].
- LCSC C165948: 136 610 uds, 0.19 USD q5 [V].
- CC1 y CC2: **pull-down Rd = 5.1 kΩ cada uno** (requisito de la spec del proyecto; consistente con
  USB Type-C para sink UFP) — 0603WAF5101T5E (C23186) [V identidad / U stock].
- VBUS de un puerto por defecto: 5 V/hasta 500 mA–3 A; con Rd fijo la placa toma 5 V por defecto,
  dentro del presupuesto de 500 mA de la spec [I].

## 5. Protección VBUS

**PPTC — Bourns MF-MSMF050-2 (1812)** [V]
- Ihold 0.50 A / Itrip 1.00 A / Vmax 15 V / Imax 100 A (datasheet Bourns, tabla p.1,
  https://www.bourns.com/docs/Product-Datasheets/mfmsmf.pdf, leído íntegro) [V].
- LCSC C17313: 9 640 uds, 0.064 USD q10 [V]. Nota: package **1812**, no 0805/1206; footprint
  `Fuse:Fuse_1812_4532Metric_Pad1.30x3.40mm_HandSolder` (existe, variante hand-solder) [V];
  símbolo `Device:Polyfuse_Small` [V].

**TVS — Littelfuse SMF5.0A (SOD-123FL)** [V]
- **Datasheet Littelfuse leído** ("TVS Diodes Surface Mount – 200W > SMF Series", Rev 05/15/20,
  captura Wayback de littelfuse.com): SMF5.0A → **VRWM 5.0 V; VBR 6.40–7.00 V @ 10 mA; IR 400 µA;
  Ipp 21.7 A; VC 9.2 V**; PPPM 200 W (10/1000 µs) / 1000 W (8/20 µs); package **SOD-123FL**
  (p.1, p.2, p.5-6) [V]. Cross-check con Vishay SMF5V0A (https://www.vishay.com/doc?85881 Rev 2.4
  p.2): mismos valores [V].
- Elegido Littelfuse por stock LCSC del fabricante genuino: C151296, 101 910 uds, 0.12 USD q5 [V].
- Compatibilidad footprint (dimensiones cotejadas): SOD-123FL Littelfuse B = 3.40–3.90 mm total con
  contacto E = 0.35–0.90 mm; KiCad `Diode_SMD:D_SMF` pads 1.3×1.4 mm @ ±1.45 mm → span exterior
  4.2 mm y gap interior 1.6 mm = B_min − 2·E_max → **cubre el package en todo el rango de
  tolerancias** [V]. Alternativa `Diode_SMD:D_SOD-123F` (span 3.9 mm, más justo). Símbolo
  `Diode:SMF5V0A` (unidireccional 5 V; su campo datasheet apunta a Vishay — discrepancia menor
  documentada).
- Honestidad sobre el clamping: la spec pide "clamping < tensión máx. de entrada del LDO" (6.5 V).
  Eso se cumple en régimen ESD/transitorios leves (clampa cerca de VBR 6.4–7.1 V), pero **a Ipp
  pleno de surge 8/20 µs el VC max es 9.2 V > 6.5 V**. Ningún TVS de 5 V en este tamaño garantiza
  <6.5 V a decenas de amperios; el PPTC aguas arriba limita la energía sostenida. Riesgo residual
  aceptado y documentado.

## 6. UI y pasivos

**LED — KT-0603R (KENTO, rojo 0603) + R serie 680 Ω** [I/V]
- Cálculo con Vf typ 2.0 V (LED rojo; datasheet KENTO no accesible → Vf [I]):
  R = (3.3 − 2.0) V / 2 mA = 650 Ω → **E24: 680 Ω** → I = 1.3/680 = **1.9 mA**.
  Con Vf 1.7–2.1 V: 1.8–2.4 mA — dentro de objetivo "~2 mA" [V el cálculo].
- LED C2286 (4.75 M uds, 0.007 USD) [V]; R 0603WAF6800T5E C23228 [V identidad / stock 0 en LCSC
  hoy → U; pieza de catálogo SMT de JLCPCB].
- KiCad: `Device:LED` + `LED_SMD:LED_0603_1608Metric`; `Device:R` + `Resistor_SMD:R_0603_1608Metric` [V].

**Botón — XKB TS-1187A-B-A-B** [V]
- Footprint oficial con nombre exacto del MPN: `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A` [V];
  símbolo `Switch:SW_Push` [V]. LCSC C318884: 1 398 460 uds, 0.02 USD q20 [V].
- Rebote: pull-up 10 kΩ (C25804) a +3V3 + 100 nF (C1591) a GND → τ = 1 ms [V valores, diseño I].

**I2C** — pull-ups 2×4.7 kΩ a +3V3 (0603WAF4701T5E, C23162): adecuado a 100 kHz con bus de
centímetros [V identidad / U stock].

**Condensadores** (valores dictados por datasheets, ver arriba):
- LDO: 2×1 µF X5R (CL10A105KB8NNNC, C15849) [V valor / U stock hoy].
- MCU: 100 nF X7R (CL10B104KB8NNNC, C1591, 483 400 uds [V]) + 4.7 µF X5R 0805
  (CL21A475KAQNNNE, C1779, 107 400 uds [V]).
- NRST: 100 nF (C1591) [V].
- LM75B VCC: 100 nF (C1591) — valor estándar, el DS no exige uno [I].

**SWD** — header genérico 1×5 2.54 mm, orden de la spec (3V3, SWDIO, SWCLK, NRST, GND);
`Connector_Generic:Conn_01x05` + `Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical` [V].
**Test points** VBUS_5V y +3V3: `Connector:TestPoint` + `TestPoint:TestPoint_Pad_1.5x1.5mm` [V].
**Montaje**: 4× `MountingHole:MountingHole_2.7mm_M2.5` [V].

---

## Hechos de datasheet para el esquemático (resumen operativo)

1. **MCU STM32G030F6P6 (TSSOP-20)** — VDD/VDDA = pin 4, VSS/VSSA = pin 5; desacoplo 100 nF + 4.7 µF
   pegado al pin 4. NRST = pin 6 con 0.1 µF a GND (pull-up interno, sin R externa). SWDIO = PA13
   (pin 18), SWCLK = PA14 (pin 19). Sin circuito BOOT0: de fábrica boot por option bytes + empty
   check → chip virgen entra al bootloader y siempre es programable por SWD. I2C1: SCL = PB6
   (pin 20), SDA = PB7 (pin 1). LED/botón en PA0..PA7 (libres).
2. **LDO AP2112K-3.3** — VIN=1, GND=2, EN=3 (atar a VIN), NC=4, VOUT=5. CIN = 1 µF y COUT = 1 µF
   cerámicos X7R/X5R exactos. Entrada máx. absoluta 6.5 V.
3. **Sensor LM75BD** — SDA=1, SCL=2, OS=3 (NC/test point), GND=4, A2=5, A1=6, A0=7 (los tres a
   GND → dirección 0x48), VCC=8 (100 nF). Temp: registro 0x00, 2 bytes, 11 bits c2, 0.125 °C/LSB,
   descartar la primera lectura tras power-up.
4. **LED**: R serie 680 Ω → ~1.9 mA con Vf 2.0 V. **Botón**: 10 kΩ pull-up + 100 nF (τ = 1 ms),
   contacto a GND. **I2C**: 2×4.7 kΩ a +3V3. **CC1/CC2**: 2×5.1 kΩ a GND (una por pin, no
   compartida). **VBUS**: conector → PPTC 500 mA → TVS 5 V → LDO, pista ≥ 0.5 mm.
