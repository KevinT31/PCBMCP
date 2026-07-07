# Arquitectura del sistema agéntico EDA — rev A 2026-07-07

> Estado: REV A — crítica adversarial propia aplicada
> (`docs/adr/ADR-0001-critica-adversarial-arquitectura.md`); contraste con Codex en
> curso, sus hallazgos se incorporan al mismo ADR.
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

**Reglas anti-divergencia (endurecidas por ADR-0001):**

1. La generación spec → KiCad ocurre **una vez por revisión** (comando explícito). Después
   del handoff, la spec NO se regenera desde KiCad ni el KiCad desde la spec.
2. **Ventana de generación y sellado.** La re-emisión completa del `.kicad_sch` desde el
   modelo del generador solo es legal DENTRO de la ventana generar → loop ERC. Al salir,
   el handoff se **sella**: commit + tag `handoff/rev_<X>` + `build/handoff_manifest.json`
   (netlist, BOM y conteos del momento del sellado). Tras el sellado, re-emitir está
   PROHIBIDO: correcciones = edición manual/auditada o nueva revisión de spec.
3. **Hash-guard.** El generador persiste el SHA-256 de cada archivo que emite
   (`build/emitted.sha256`). Antes de re-emitir compara contra el archivo en disco; si
   difieren, aborta ("ediciones externas detectadas") — nunca sobreescribe trabajo manual.
4. **Regla de escritor único.** En todo momento un solo actor (generador ∨ humano-GUI ∨
   herramienta auditada) escribe los archivos KiCad. Toda escritura scriptada comprueba
   antes el lockfile de KiCad (`~*.lck`).
5. La spec pasa a ser **contrato de verificación**: `pcb-ai verify-spec` hace dos
   comparaciones — spec↔KiCad (contrato: rails, interfaces, nets críticas, prohibidos)
   y manifest↔KiCad (deriva desde el sellado: adiciones/eliminaciones se alertan).
   El drift no se "sincroniza": se reporta y un humano/agente decide dónde corregir.
   **Límites explícitos** — verify-spec NO detecta: valores plausibles pero incorrectos,
   footprints equivocados no fijados por la spec, ni reglas físicas del `.kicad_pcb`.
   Un verify-spec verde no es validación eléctrica; eso es ERC/DRC/simulación/red-team.
6. Cambio de requisitos = nueva revisión de la spec + regeneración o edición manual
   documentada (ADR corto en `docs/adr/`).

## 2. Pipeline y mecanismos por etapa

```text
design_spec.yaml ──validate──► arquitectura eléctrica (docs) ──► selección componentes (evidencia)
      │
      ▼ (handoff único por revisión)
GENERADOR DE ESQUEMÁTICO (Python: kicad-sch-api SOLO en modo creación ▸ fallback plantillas S-expr)
      │  pipeline defensivo: generar → kicad-cli sch upgrade → sch erc --format json → export pdf
      │  REGLA (TESTED 2026-07-06, reports/smoke/kicad_sch_api_roundtrip.md):
      │  · crear archivos nuevos: APTO (parseables por KiCad 10)
      │  · editar .kicad_sch v10 existentes: NO APTO (roundtrip cambia 5638/3545 líneas
      │    y altera ERC 43→90) → el loop de reparación edita el MODELO del generador
      │    y re-emite el archivo completo; nunca se parchea el archivo en sitio
      ▼
PROYECTO KICAD = SOURCE OF TRUTH
      │
      ├─ ERC loop:      kicad-cli sch erc (JSON) → clasificar → reparar → repetir
      │                 Terminales: VERDE (0 violaciones no suprimidas) · ESTANCADO
      │                 (2 iter. sin reducción estricta) · AGOTADO (tope 5). ESTANCADO/
      │                 AGOTADO → reporte + humano; no existe "verde parcial". PROHIBIDO
      │                 añadir exclusions automáticamente (se cuentan violaciones PRE-exclusion).
      ├─ Simulación:    kicad-cli sch export netlist --format spice → ngspice 46 batch
      ├─ BOM/sourcing:  kicad-cli sch export bom + validaciones pcb-ai
      ├─ PCB:           SWIG pcbnew headless (placement scriptado) + GUI para routing crítico
      │                 FreeRouting 2.2.4 (Temurin 25) solo nets no críticas, si el smoke test DSN pasa
      │                 AISLAMIENTO (ADR-0001 H5): todo acceso SWIG vive en app/pcb_ai/pcb_backend.py;
      │                 el resto del pipeline importa pcb_backend, nunca pcbnew → migración
      │                 a IPC/kipy (KiCad 11) = swap de backend, no reescritura
      ├─ DRC loop:      kicad-cli pcb drc (JSON) → clasificar → reparar → repetir
      │                 (mismos terminales y anti-trampa que el ERC loop)
      ├─ Red team:      revisión hostil independiente de ERC/DRC (agente red-team-hardware)
      └─ Fabricación:   kicad-cli pcb export gerbers/drill/pos + validaciones de paquete
```

**Roles del LLM vs deterministas:** Claude Code (y subagentes) proponen, generan código y
clasifican reportes; **toda validación eléctrica pasa por herramientas deterministas**
(kicad-cli, ngspice, scripts de cálculo con unidades). Un resultado "verde" solo puede
afirmarse citando el reporte generado.

## 3. Capa MCP (reducida por ADR-0001 H4)

- **Seeed kicad-mcp-server**: capa de LECTURA + ERC/DRC. Tools de escritura bloqueadas
  por `permissions.deny` en `.claude/settings.json`. Único MCP del plan activo.
- **mixelpixx KiCAD-MCP-Server v2.3.1 (pineado)**: **DIFERIDO**. Escribe con su propio
  serializador — misma clase de riesgo que descalificó a kicad-sch-api para edición
  in-place — y añade un tercer escritor potencial. Solo se instalará si aparece una
  necesidad interactiva real, y entonces: validación previa en `sandbox/` con git,
  `KICAD_BACKEND=swig`, GUI cerrada, `permissions.ask` en escrituras, tools de
  sourcing JLCPCB nunca invocadas (salida de red a terceros).
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
| kicad-sch-api: RESUELTO por smoke test (2026-07-06) — apto solo creación, no edición in-place | Nueva versión de kicad-sch-api que declare KiCad 10 |
| FreeRouting DSN headless vía SWIG | Smoke test; si falla, routing no crítico también manual |
| Java 25 solo para FreeRouting | Instalar Temurin 25 aislado, sin tocar JAVA_HOME global |

## 6. Validación de esta arquitectura

1. ✔ Crítica adversarial propia (2026-07-07): hallazgos y decisiones en
   `docs/adr/ADR-0001-critica-adversarial-arquitectura.md`. Contraste con Codex en
   curso; sus hallazgos se incorporan al mismo ADR.
2. Pendiente: smoke tests locales de §5 (FreeRouting DSN; lib_symbols embebidos del
   generador — se cierra con el primer esquemático del demostrador).
3. El demostrador end-to-end es la prueba final: si una etapa no puede completarse
   con el mecanismo elegido, se aplica la cadena de fallback documentada en
   `docs/research/kicad_automation_stack.md` §4 y se registra ADR.
