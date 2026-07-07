# SMF5.0A (Littelfuse) — hechos de datasheet

Fuente primaria: "TVS Diodes — Surface Mount – 200W > SMF Series", Littelfuse, Rev 05/15/20.
URL oficial: https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smf_datasheet.pdf.pdf
(leído íntegro vía captura Wayback Machine de esa URL; littelfuse.com bloquea esta red).
Cross-check: Vishay SMF5V0A, https://www.vishay.com/doc?85881 Rev 2.4 (leído directo) — mismos valores.

## Identidad y package
- SMF5.0A = TVS **unidireccional** 5 V de la serie SMF; package **SOD-123FL**, "plastic over glass
  passivated junction", banda = cátodo. [DS p.1, p.5] — VERIFIED
- Ordering: SMF5.0A (T&R 3000/carrete 7") o SMF5.0A-T13 (10000/13"). [DS p.6] — VERIFIED
- LCSC 2026-07-07: C151296 (Littelfuse genuino) stock 101 910, 0.1197 USD q5. API LCSC. — VERIFIED

## Eléctricos (SMF5.0A) [DS p.2, tabla] — VERIFIED
| Parámetro | Valor |
|---|---|
| VRWM (working stand-off) | **5.0 V** |
| VBR @ IT=10 mA | 6.40–7.00 V |
| IR @ VRWM | 400 µA max |
| Ipp (10/1000 µs) | 21.7 A |
| VC @ Ipp | **9.2 V max** |
| PPPM | 200 W (10/1000 µs); 1000 W (8/20 µs) [p.1] |
| TJ | −65…+150 °C [p.1] |

## Aplicación en demo-vigia
- VRWM 5.0 V ≥ VBUS nominal 5 V (rango spec 4.5–5.5 V: a 5.5 V hay conducción de fuga parcial por
  encima de VRWM — típico en TVS de 5 V sobre VBUS; IR especificado solo a 5.0 V). — VERIFIED (dato) / INFERRED (valoración)
- Clamping: en ESD/transitorios leves clampa cerca de VBR (6.4–7.0 V); **a Ipp pleno VC = 9.2 V >
  6.5 V (abs max del AP2112)** → riesgo residual solo en surge severo; el PPTC aguas arriba limita
  la energía sostenida. Decisión documentada en docs/component_selection.md §5. — VERIFIED (datos) / INFERRED (aceptación de riesgo)

## KiCad
- Símbolo: `Diode:SMF5V0A` (TVS unidireccional 5 V, gráfico correcto; su campo Datasheet apunta al
  doc de Vishay — discrepancia menor de MPN documentada). — VERIFIED (existencia local)
- Footprint: `Diode_SMD:D_SMF` — pads 1.3×1.4 mm @ ±1.45 mm → span exterior 4.2 mm, gap interior
  1.6 mm; SOD-123FL Littelfuse: largo total B = 3.40–3.90 mm, contacto E = 0.35–0.90 mm →
  gap ≥ B_min − 2·E_max = 1.60 mm. Compatible en todo el rango de tolerancias. [DS p.5 + medida
  del .kicad_mod local] — VERIFIED
- Alternativa: `Diode_SMD:D_SOD-123F` (span 3.9 mm, más justo). — VERIFIED (existencia local)
