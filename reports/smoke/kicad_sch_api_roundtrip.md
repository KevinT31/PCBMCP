# Smoke test kicad-sch-api vs formato KiCad 10

- Carga y re-guardado: **OK**
- ERC original: exit=0, violaciones=43
- ERC roundtrip: exit=0, violaciones=90
- **ADVERTENCIA: el número de violaciones cambió (43 → 90)** — el roundtrip altera semántica
- Diff textual: 5638 líneas cambiadas de 3545

- Creación desde cero (2 R + wire): **OK guardado**
- ERC sobre el creado: exit=0, violaciones=4 → **parseable por KiCad 10**

## Veredicto: NO APTO — usar fallback