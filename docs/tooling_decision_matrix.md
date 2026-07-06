# Matriz de decisión de tooling — julio 2026

Síntesis de tres investigaciones independientes (2026-07-06):
`docs/research/kicad_automation_stack.md` · `docs/research/mcp_kicad_survey.md` · `docs/research/ai_eda_commercial.md`

**Leyenda de celdas:** ✔ = capacidad verificada · ◐ = parcial/condicionada · ✘ = no tiene · ? = sin verificar.
**Confianza:** V=VERIFIED (docs oficiales/código/issues), I=INFERRED, U=UNVERIFIED. Cada fila cita su evidencia en las notas.

## Matriz principal

| Herramienta | Schematic AI | Schematic Write | PCB Write | Placement | Routing | SPICE | BOM | API | MCP | Local | Git-friendly | Madurez | Riesgo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **KiCad 10.0.x** (base) | ✘ | ◐ GUI/terceros (V) | ✔ GUI + SWIG (V) | manual | interactivo (V) | ◐ solo GUI (V) | ✔ cli (V) | ◐ IPC solo PCB+GUI (V) | vía terceros | ✔ | ✔ texto s-expr (V) | Alta (V) | Bajo |
| **kicad-cli 10** | ✘ | ✘ (V) | ✘ (V) | ✘ | ✘ | ◐ exporta netlist spice (V) | ✔ (V) | n/a | n/a | ✔ | ✔ JSON reports (V) | Alta (V) | Bajo |
| **IPC API / kipy 0.7** | ✘ | ✘ hasta v11 (V) | ✔ con GUI abierta (V) | ◐ | ◐ | ✘ | ✘ | ✔ | n/a | ✔ | n/a | Media (V) | Medio: exige GUI, cobertura solo PCB |
| **SWIG pcbnew** | ✘ | ✘ | ✔ headless (V) | ◐ scriptable | ◐ | ✘ | ◐ | ✔ py | n/a | ✔ | n/a | Alta pero **muere en KiCad 11** (V) | Medio: deuda programada |
| **kicad-sch-api / circuit-synth** | ◐ diseñado para LLM (V) | ✔ declara KiCad 7/8; **v10 sin declarar** (V/U) | ✘ | ✘ | ✘ | ✘ | ◐ | ✔ py | ✔ propio (estancado) | ✔ | ✔ | Joven (V) | Medio: validar roundtrip v10 |
| **kicad-skip** | ✘ | ◐ | ◐ | ✘ | ✘ | ✘ | ✘ | ✔ py | ✘ | ✔ | ✔ | **Estancado 2+ años** (V) | Alto para v10 |
| **kiutils** | ✘ | ◐ ≤v8 (V) | ◐ ≤v8 | ✘ | ✘ | ✘ | ✘ | ✔ py | ✘ | ✔ | ✔ | Estancado (V) | Alto: dataclasses rompen con v10 (I) |
| **SKiDL 2.2.3** | ◐ código→circuito | ◐ netlist sí; .kicad_sch visual contradictorio (V/U) | ✘ | ✘ | ✘ | ◐ | ◐ | ✔ py | ✘ | ✔ | ✔ | Activa; KiCad 5–9, v10 sin declarar (V) | Medio: doble source of truth (I) |
| **S-expr directas (plantillas)** | ✘ | ✔ control total | ✔ | ✘ | ✘ | ✘ | ✘ | n/a | n/a | ✔ | ✔ | n/a | Medio: coste desarrollo + corrupción si mal hecho |
| **MCP mixelpixx v2.3.1** | ◐ vía LLM | ✔ 25 tools sch (V) | ✔ (V) | ◐ tools | ◐ + FreeRouting (V) | ✘ | ✔ | n/a | ✔ | ✔ | ✔ backups `.mcp-backups/` (V) | Media-alta, muy activo (V) | Medio: historial corrupción <2.3.0 corregido; red a jlcsearch de terceros (V); **sin ERC** (V) |
| **MCP Seeed** | ✘ | ◐ experimental, bug #9 abierto (V) | ✘ | ✘ | ✘ | ✘ | ◐ | n/a | ✔ | ✔ | ✔ | Media (V) | Bajo en solo-lectura; **ERC+DRC** (V) |
| **kicad-mcp-pro** | ◐ | ✔ transaccional (V) | ✔ | ◐ | ◐ | ◐ | ✔ | n/a | ✔ | ✔ | ✔ | **5 semanas, 17★** (V) | Alto por inmadurez; mejor seguridad del grupo (V) |
| **FreeRouting 2.2.4** | ✘ | ✘ | ✘ | ✘ | ✔ batch DSN/SES (V) | ✘ | ✘ | ✔ REST beta (V) | ✔ beta | ✔ | n/a | Media (V) | Medio: exige **Java 25** (V); DSN headless depende de SWIG (I); calidad variable (I) |
| **ngspice 46** | ✘ | ✘ | ✘ | ✘ | ✘ | ✔ batch (V) | ✘ | ◐ DLL | ✘ | ✔ | ✔ | Alta (V) | Bajo; no está en winget (V) |
| **Flux.ai** | ✔ (calidad cuestionada por usuarios, V) | ✔ en su cloud | ✔ en su cloud | ✔ | ✔ | ◐ | ✔ | ✘ sin API pública (V) | ✘ | ✘ cloud-only (V) | ✘ | Media | **Alto**: lock-in, export solo Gerber, proyectos gratis públicos, conflicto Adafruit (V) |
| **Quilter** | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ | ✘ | ✘ pública (V) | ✘ | ◐ self-host enterprise (V) | ◐ devuelve KiCad nativo (V) | Media (V) | Medio: cloud/IP, pago por pin, vías pasantes solo (V) |
| **JITX** | ◐ código+LLM (V) | ✔ en su stack | ✔ | ✔ | ✔ | ◐ | ◐ | ✔ Python (V) | ? | ◐ | ◐ exporta KiCad (V) | Early-access (V) | Medio-alto: acceso limitado, sin reviews independientes (V) |
| **atopile 0.15.x** | ◐ `.ato` | ◐ genera netlist/pcb | ✔ actualiza .kicad_pcb (V) | ✘ | ✘ | ✘ | ✔ picking (V) | ✔ | ✘ | ✔ | ✔ | Pre-1.0 activa (V) | Medio: exige Python 3.14 (V); lenguaje propio = curva |
| **tscircuit** | ◐ React+AI (V) | ◐ export KiCad (V) | ◐ | ◐ | ◐ + DSN (V) | ✘ | ✔ | ✔ TS | ✔ | ✔ | ✔ | Activa; DRC/autoroute en desarrollo (V) | Medio: TypeScript como fuente = otra fuente de verdad |

## Decisiones derivadas (criterio → evidencia → confianza)

1. **KiCad 10.0.x como plataforma base.** Criterio: cubre ERC/DRC/fabricación headless con JSON + exit codes; los dos MCP finalistas lo soportan; formato s-expr en texto = git-friendly. Evidencia: docs.kicad.org/10.0/cli, survey MCP §5. Confianza: V.
2. **kicad-cli como columna vertebral de validación/exportación** (no negociable). Evidencia: stack §2. Confianza: V.
3. **Escritura de esquemático: kicad-sch-api con pipeline defensivo** (generar → `sch upgrade` → ERC JSON → PDF), fallback S-expr por plantillas. Riesgo v10 abierto → smoke test local obligatorio antes de adoptar. Evidencia: stack §4, §9.1-2. Confianza: decisión I, capacidad U hasta probar.
4. **PCB headless: SWIG pcbnew del Python embebido de KiCad**, sabiendo que desaparece en v11 (deuda documentada, re-evaluar con KiCad 11 ≈ mar-2027). Evidencia: stack §3. Confianza: V (deprecación), I (idoneidad).
5. **MCP: mixelpixx v2.3.1 (escritura, pineado) + Seeed (lectura/ERC/DRC)**, instalación por fases con sandbox git y `permissions.deny/ask`. Evidencia: survey §5. Confianza: V (auditoría de código).
6. **SKiDL fuera del camino crítico.** Riesgo de doble fuente de verdad + generación visual contradictoria + v10 sin declarar. Queda como validador opcional de conectividad si la generación directa falla. Evidencia: stack §5. Confianza: I.
7. **Simulación: ngspice 46 standalone en batch** + netlist spice de kicad-cli (calidad del netlist U → probar). Evidencia: stack §7. Confianza: V/U.
8. **Routing: interactivo para nets críticas; FreeRouting 2.2.4 evaluable para no críticas** (requiere Temurin 25 aparte del Java 21 actual; paso DSN headless por SWIG a probar). Evidencia: stack §6. Confianza: V (requisitos), U (flujo headless completo).
9. **Flux.ai descartado; Quilter y JITX en fase futura** (reevaluar en 6-12 meses); atopile/tscircuit en observación, no en camino crítico. Evidencia: ai_eda_commercial.md. Confianza: V.
10. **APIs de componentes: sin credenciales por ahora**; datasheets de fabricante como fuente primaria + catálogo JLCPCB vía herramientas locales cuando aplique. Evidencia: ai_eda_commercial.md §APIs. Confianza: V.
