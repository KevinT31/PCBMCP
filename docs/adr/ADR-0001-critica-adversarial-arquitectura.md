# ADR-0001 — Crítica adversarial de la arquitectura (rev provisional 2026-07-06)

- **Fecha:** 2026-07-07
- **Estado:** Aceptado (crítica propia de Claude; contraste con Codex en curso — ver §Contraste)
- **Contexto:** `docs/architecture.md` quedó marcada PROVISIONAL pendiente de crítica
  adversarial. El usuario decidió (2026-07-06): Claude critica ahora, Codex contrasta
  cuando su cuota lo permita. Este ADR registra los hallazgos, su severidad y las
  decisiones aplicadas a `docs/architecture.md`.

## Hallazgo 1 — CRÍTICO: re-emisión completa vs ediciones manuales post-handoff

**Problema.** La arquitectura dice a la vez: (a) tras el handoff, el proyecto KiCad es
autoritativo y "editable a mano (GUI o herramientas auditadas)"; (b) el loop de
reparación ERC "edita el MODELO del generador y re-emite el archivo completo". Si un
humano edita el `.kicad_sch` en la GUI y después cualquier proceso re-emite el archivo
desde el modelo, **las ediciones manuales se pierden en silencio**. Es exactamente la
clase de divergencia silenciosa que la opción E pretendía eliminar.

**Decisión (aplicada).**
1. **Sellado de handoff.** La re-emisión completa solo es legal DENTRO de la ventana
   de generación (generar → loop ERC → verde/estancado). Al salir de esa ventana el
   handoff se "sella": commit + tag `handoff/rev_<X>` y snapshot de manifest (ver H2).
   Tras el sellado, re-emitir está PROHIBIDO; correcciones = edición manual/auditada
   o nueva revisión de spec (nuevo ADR + nueva ventana de generación).
2. **Hash-guard determinista.** El generador guarda el SHA-256 del último archivo que
   emitió (`build/emitted.sha256`). Antes de cualquier re-emisión compara el hash del
   archivo en disco: si difiere → aborta con error "ediciones externas detectadas",
   nunca sobreescribe. Candado barato, sin heurísticas.
3. **Git como red.** Commit automático antes de cada re-emisión dentro de la ventana.

## Hallazgo 2 — CRÍTICO: puntos ciegos estructurales de `verify-spec`

**Problema.** `verify-spec` compara la spec contra hechos extraíbles por kicad-cli
(netlist/BOM). Clases de drift que NO puede detectar:
- **Drift inverso:** componentes/nets AÑADIDOS al proyecto que la spec no menciona no
  violan ninguna aserción (la spec dice qué debe existir, no qué no debe).
- Valores incorrectos pero plausibles (divisor con resistencias intercambiadas).
- Footprint/variante de package equivocados si la spec no los fija.
- Reglas físicas (clearance de nets críticas) que viven en el `.kicad_pcb`, no en netlist.

**Decisión (aplicada).**
1. **Manifest de handoff.** En el sellado se guarda `build/handoff_manifest.json`:
   netlist + BOM + conteos (componentes, nets, hojas) del momento del handoff.
   `verify-spec` pasa a hacer DOS comparaciones: spec↔KiCad (contrato) y
   manifest↔KiCad (deriva desde el sellado). Las adiciones/eliminaciones se ALERTAN
   aunque no puedan juzgarse; un humano decide.
2. **Lista explícita de no-detectables** en `docs/architecture.md` §verify-spec, para
   que nadie trate un verify-spec verde como validación eléctrica. La validación
   eléctrica sigue siendo ERC/DRC/simulación/red-team.

## Hallazgo 3 — MEDIO: el loop ERC/DRC no define progreso, terminación ni anti-trampa

**Problema.** "Máx. 5 iteraciones" no dice: qué pasa si el conteo de violaciones
oscila (A→B→A) o no baja; qué estado se declara al agotar; y — lo más peligroso con
un LLM en el loop — nada prohíbe "reparar" añadiendo **exclusions/waivers** de KiCad,
que ponen el reporte en verde sin arreglar nada.

**Decisión (aplicada).**
1. Estados terminales del loop: **VERDE** (0 violaciones no suprimidas), **ESTANCADO**
   (2 iteraciones consecutivas sin reducción estricta del conjunto de violaciones),
   **AGOTADO** (tope de 5). ESTANCADO y AGOTADO → reporte clasificado + intervención
   humana. No existe "verde parcial".
2. **Prohibido añadir exclusions automáticamente.** Toda exclusion/waiver requiere
   decisión humana documentada (ADR corto o nota en el reporte de la revisión).
   El comparador del loop cuenta violaciones ANTES de aplicar exclusions.

## Hallazgo 4 — MEDIO: la capa MCP dual amplía superficie sin necesidad actual

**Problema.** mixelpixx escribe `.kicad_sch/.kicad_pcb` vía su propio serializador —
la misma clase de riesgo que descalificó a kicad-sch-api para edición in-place
(roundtrip destructivo). Además: tres escritores potenciales (MCP escritura, GUI,
generador), y la regla "GUI cerrada durante escrituras" no es verificable por el MCP.
Todo esto para una capa que la propia arquitectura declara "conveniencia interactiva".

**Decisión (aplicada).**
1. **Regla de escritor único:** en todo momento exactamente un actor tiene permiso de
   escritura sobre los archivos KiCad. Se materializa con: comprobación del lockfile
   de KiCad (`~*.lck`) antes de cualquier escritura scriptada + hash-guard (H1) +
   convención de fases.
2. **Capa MCP reducida:** se instala solo **Seeed en modo lectura + ERC/DRC** (riesgo
   bajo verificado). **mixelpixx (escritura) queda DIFERIDO** hasta que exista una
   necesidad interactiva real; si se instala, solo en `sandbox/` con git y `permissions.ask`.
   La tarea #4 se reduce en alcance, no se elimina.

## Hallazgo 5 — MEDIO: la deuda SWIG→IPC no está aislada en el código

**Problema.** La deuda está documentada (KiCad 11 ≈ 2027 elimina SWIG) pero nada
impide que llamadas `pcbnew.*` se dispersen por el pipeline, convirtiendo la migración
futura en reescritura.

**Decisión (aplicada).** Todo acceso a SWIG pcbnew vive en UN módulo:
`app/pcb_ai/pcb_backend.py`, con API estrecha orientada a intención
(cargar_placa, colocar_componente, exportar_dsn, correr_drc…). El resto del pipeline
importa `pcb_backend`, nunca `pcbnew`. La migración a IPC/kipy será un swap de backend.

## Hallazgo 6 — BAJO (riesgo conocido, se resuelve empíricamente en fase 4)

`kicad-cli sch erc` sobre archivos creados por kicad-sch-api depende de que el
generador embeba correctamente `lib_symbols`. Si no, ERC fallará con "symbol not
found" aunque el archivo sea parseable. Mitigación ya prevista: fallback a plantillas
S-expr con `lib_symbols` copiados de las librerías oficiales de KiCad 10. Se valida
con el primer esquemático real del demostrador.

## Qué se evaluó y NO se cambió

- **Source of truth híbrido por fases (opción E):** se mantiene. La alternativa
  (spec siempre autoritativa) reintroduce sync bidireccional; la crítica no encontró
  un caso que la opción E + sellado + manifest no cubra mejor.
- **Tope de 5 iteraciones:** se mantiene como tope duro; ESTANCADO suele disparar antes.
- **kicad-cli como columna de validación:** sin objeciones; es la parte más sólida.

## Contraste con Codex

Revisión adversarial de Codex lanzada 2026-07-07 (task en background). Cuando llegue:
se registran aquí los hallazgos que difieran o se sumen, con decisión explícita
aplicar/ignorar. Si Codex no aporta hallazgos nuevos de severidad ≥ media, la
arquitectura queda aprobada sin nueva revisión.

### Resultado del contraste

_Pendiente de que termine el task de Codex — se completa en esta misma sesión._
