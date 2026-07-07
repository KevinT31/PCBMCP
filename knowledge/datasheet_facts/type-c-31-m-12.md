# TYPE-C-31-M-12 (HRO / Korean Hroparts Elec) — hechos del plano del fabricante

Fuente primaria: plano oficial HRO ELECTRONICS CO., LTD, "TYPE-C-31-M-12", Rev A, 2015.5.13,
dibujado por JKUN.LU, ROHS.
URL oficial: http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf — la misma URL que cita el
metadato del footprint oficial de KiCad. Leído íntegro vía captura Wayback Machine (krhro.com
devuelve 403 desde esta red). Plano rasterizado e inspeccionado visualmente.

## Identidad
- Receptáculo USB Type-C hembra, variante **16 contactos (USB 2.0)**, montaje SMD con anclajes.
- LCSC 2026-07-07: C165948 stock 136 610, 0.1857 USD q5. API LCSC. — VERIFIED

## Tabla de pines [plano, tabla PIN/SIGNAL NAME] — VERIFIED
| Pin | Señal | Pin | Señal |
|---|---|---|---|
| A1 | GND | B12 | GND |
| A4 | VBUS | B9 | VBUS |
| A5 | **CC1** | B8 | SBU2 |
| A6 | DP1 | B7 | DN2 |
| A7 | DN1 | B6 | DP2 |
| A8 | SBU1 | B5 | **CC2** |
| A9 | VBUS | B4 | VBUS |
| A12 | GND | B1 | GND |

- Para power-only: VBUS = A4/A9/B4/B9 unidos; GND = A1/A12/B1/B12 + shield; CC1 (A5) y CC2 (B5)
  cada uno con Rd = 5.1 kΩ a GND (una resistencia por pin, no compartida); DP/DN/SBU sin conectar. — INFERRED (aplicación; pines VERIFIED)

## Eléctrico/mecánico [plano, notas] — VERIFIED
- Corriente nominal: **3 A min en VBUS**; 0.25 A min en el resto de contactos.
- Resistencia de contacto: 40 mΩ max. Aislamiento: 100 MΩ min. Rigidez dieléctrica: 250 V AC.
- Vida: 10 000 ciclos de inserción. Fuerza de extracción: 2.0 kgf max / 0.8 kgf min.
- Temperatura de trabajo: −55…+85 °C.
- Materiales: LCP+30 %GF UL94V-0; terminales aleación de cobre C5191; carcasa inox T = 0.30 mm.
- Dimensiones principales: cuerpo 8.94 ± 0.15 mm ancho; profundidad 7.30 ± 0.15 mm; incluye
  "Recommended P.C.B. layout" con 16 pads de paso fino y 4 anclajes (2×2.10/2×1.70 y ovales 4×1.00).

## KiCad
- Símbolo: `Connector:USB_C_Receptacle_USB2.0_16P`. — VERIFIED (existencia local)
- Footprint: `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` — 17 pads nombrados A1-A12/B1-B12
  (subconjunto 16P) + SH; el descr del footprint cita exactamente este plano. — VERIFIED (en disco)
