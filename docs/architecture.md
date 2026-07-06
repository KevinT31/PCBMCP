# Arquitectura del sistema agéntico EDA — rev provisional 2026-07-06

> Estado: PROVISIONAL — pendiente de crítica adversarial (Codex) y de los smoke tests
> que cierran los puntos UNVERIFIED de `docs/research/kicad_automation_stack.md` §9.
> Base de evidencia: `docs/tooling_decision_matrix.md`.

## 1. Decisión central: source of truth híbrido explícito por fases (opción E)

La hipótesis original ("KiCad como source of truth único") se refina: **ningún artefacto
único puede ser autoritativo en todas las fases** sin crear divergencia silenciosa.
La resolución es un **contrato por fases con transferencia de autoridad explícita e
irreversible** (sin sincronización bidireccional, que es donde nace el drift):

| Fase | Artefacto autoritativo | Se genera desde él | Editable a mano |
|---|---|---|---|
| Requisitos | `spec/design_spec.yaml` (validado por schema) | docs de arquitectura, plan de componentes | Sí (es la entrada) |
| Componentes | `bom/component_candidates.csv` + `knowledge/datasheet_facts/` | selección para el esquemático | Sí, con evidencia |
| **Esquemático en adelante** | **Proyecto KiCad** (`.kicad_sch`, `.kicad_pcb`) | netlist, BOM, gerbers, reports | Sí (GUI o herramientas auditadas) |

**Reglas anti-divergencia:**

1. La generación spec → KiCad ocurre **una vez por revisión** (comando explícito). Después
   del handoff, la spec NO se regenera desde KiCad ni el KiCad desde la spec.
2. La spec pasa a ser **contrato de verificación**: `pcb-ai verify-spec` extrae del proyecto
   KiCad (netlist/BOM vía kicad-cli) los hechos comprobables — rails presentes, interfaces,
   nets críticas con regla asignada, componentes prohibidos ausentes — y reporta drift.
   El drift no se "sincroniza": se reporta y un humano/agente decide dónde corregir.
3. Cambio de requisitos = nueva revisión de la spec + regeneración o edición manual
   documentada (ADR corto en `docs/adr/`).

## 2. Pipeline y mecanismos por etapa

```text
design_spec.yaml ──validate──► arquitectura eléctrica (docs) ──► selección componentes (evidencia)
      │
      ▼ (handoff único por revisión)
GENERADOR DE ESQUEMÁTICO (Python: kicad-sch-api ▸ fallback plantillas S-expr)
      │  pipeline defensivo: generar → kicad-cli sch upgrade → sch erc --format json → export pdf
      ▼
PROYECTO KICAD = SOURCE OF TRUTH
      │
      ├─ ERC loop:      kicad-cli sch erc (JSON) → clasificar → reparar → repetir (máx. 5 iter.)
      ├─ Simulación:    kicad-cli sch export netlist --format spice → ngspice 46 batch
      ├─ BOM/sourcing:  kicad-cli sch export bom + validaciones pcb-ai
      ├─ PCB:           SWIG pcbnew headless (placement scriptado) + GUI para routing crítico
      │                 FreeRouting 2.2.4 (Temurin 25) solo nets no críticas, si el smoke test DSN pasa
      ├─ DRC loop:      kicad-cli pcb drc (JSON) → clasificar → reparar → repetir
      ├─ Red team:      revisión hostil independiente de ERC/DRC (agente red-team-hardware)
      └─ Fabricación:   kicad-cli pcb export gerbers/drill/pos + validaciones de paquete
```

**Roles del LLM vs deterministas:** Claude Code (y subagentes) proponen, generan código y
clasifican reportes; **toda validación eléctrica pasa por herramientas deterministas**
(kicad-cli, ngspice, scripts de cálculo con unidades). Un resultado "verde" solo puede
afirmarse citando el reporte generado.

## 3. Capa MCP (plan controlado, survey §5)

- **Seeed kicad-mcp-server**: capa de LECTURA + ERC/DRC. Tools de escritura bloqueadas
  por `permissions.deny` en `.claude/settings.json`.
- **mixelpixx KiCAD-MCP-Server v2.3.1 (pineado)**: escritura, solo tras validar en
  `sandbox/` con git; `KICAD_BACKEND=swig`, KiCad GUI cerrada durante escrituras;
  `permissions.ask` en tools de escritura; tools de sourcing JLCPCB no invocadas
  (salida de red a terceros).
- El MCP es **conveniencia interactiva**; el pipeline reproducible (CLI `pcb-ai`) no
  depende de MCPs: todo lo crítico corre por kicad-cli/Python directamente.

## 4. Qué se descartó y por qué (resumen; detalle en la matriz)

- **Flux.ai**: cloud-only, sin export editable a KiCad, sin API, señales de confianza negativas. Descartado.
- **SKiDL en el camino crítico**: doble fuente de verdad + generación visual inmadura. Queda como validador opcional.
- **kicad-skip / kiutils**: sin mantenimiento frente a formato v10.
- **IPC API (kipy) hoy**: exige GUI y solo PCB; se adopta cuando KiCad 11 la haga headless (≈2027) — sustituirá a SWIG.
- **Quilter/JITX**: fase futura (reevaluación 6-12 meses).
- **atopile/tscircuit**: en observación; introducirían otra fuente de verdad.

## 5. Deuda técnica programada (explícita)

| Deuda | Detonante de revisión |
|---|---|
| SWIG pcbnew desaparece en KiCad 11 | Release KiCad 11 (~mar-2027): migrar a IPC API headless |
| kicad-sch-api declara KiCad 7/8 | Smoke test roundtrip v10 (bloqueante antes de adoptar) |
| FreeRouting DSN headless vía SWIG | Smoke test; si falla, routing no crítico también manual |
| Java 25 solo para FreeRouting | Instalar Temurin 25 aislado, sin tocar JAVA_HOME global |

## 6. Validación pendiente de esta arquitectura

1. Crítica adversarial (Codex, Caso B) — registrar hallazgos y decisiones.
2. Smoke tests locales de §5 (cierran los UNVERIFIED).
3. El demostrador end-to-end es la prueba final: si una etapa no puede completarse
   con el mecanismo elegido, se aplica la cadena de fallback documentada en
   `docs/research/kicad_automation_stack.md` §4 y se registra ADR.
