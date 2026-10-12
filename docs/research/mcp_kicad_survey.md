# Auditoría de servidores MCP para KiCad (julio 2026)

**Autor:** mcp-scout-security · **Fecha:** 2026-07-06 · **Entorno objetivo:** Windows 11 Home x64, 16 GB RAM, cliente MCP, Python 3.12.5, Node 22, uv. KiCad aún no instalado.

**Método:** código fuente clonado (`git clone --depth 1` en `%TEMP%\mcp-scout`), API de GitHub (stars/issues/fechas), issues reales y docs oficiales de KiCad. No se instaló ni configuró nada.

**Etiquetas de confianza:** `VERIFIED` = código leído / docs oficiales / API GitHub · `INFERRED` = deducción razonada · `UNVERIFIED` = solo README/marketing.

---

## 1. Contexto técnico: cómo puede un MCP hablar con KiCad

| Mecanismo | Estado (VERIFIED, docs.kicad.org) | Implicación |
|---|---|---|
| `kicad-cli` | ERC/DRC/exportaciones headless desde KiCad 7+; incluido en toda instalación | La vía más segura y estable; no requiere GUI |
| SWIG `pcbnew` (Python) | Existe en KiCad 9 y 10; **se elimina en KiCad 11** | Headless, pero deprecado; solo PCB, no esquemático |
| IPC API oficial (`kipy` / paquete `kicad-python`) | En KiCad 9/10 **requiere la GUI abierta** con API server habilitado; headless solo desde KiCad 11 | Es el futuro oficial, pero hoy exige KiCad corriendo |
| Manipulación directa de S-expressions (.kicad_sch/.kicad_pcb) | Sin API: parsing/escritura de texto | Máximo riesgo de corrupción si el formato no se respeta byte a byte |

Conclusión para elegir versión de KiCad: **KiCad 9 o 10** cubren los cuatro mecanismos; los dos candidatos finalistas soportan ambas explícitamente (VERIFIED). Recomendación abajo (§5).

---

## 2. Tabla comparativa

| Criterio | lamaalrajih/kicad-mcp | Seeed-Studio/kicad-mcp-server | mixelpixx/KiCAD-MCP-Server | oaslananka/kicad-mcp (`kicad-mcp-pro`) | circuit-synth/mcp-kicad-sch-api |
|---|---|---|---|---|---|
| Licencia | MIT (VERIFIED) | MIT en pyproject, **sin archivo LICENSE** (VERIFIED) | MIT (VERIFIED) | MIT (VERIFIED) | MIT (VERIFIED) |
| Lenguaje | Python | Python | TypeScript (servidor) + Python (motor) | Python | Python |
| Stars / issues abiertas | 481 / 28 | 58 / 4 | 1 454 / 25 | 17 / 0 | 20 / 2 |
| Último push (VERIFIED API) | **2025-10-17 (estancado)** | 2026-05-22 | **2026-07-06 (hoy)** | 2026-07-05 | 2025-08-20 (estancado) |
| Release | — | — | v2.3.1 (jul 2026) | v3.19.0 (jul 2026) | v0.x |
| Lectura sch/pcb | Sí | Sí (la mejor relación simplicidad/valor) | Sí | Sí | Solo sch |
| Escritura sch/pcb | **No** (solo reportes/BOM) | Experimental, sin backups | Sí, ~120 tools, con backups rotativos | Sí, transaccional con rollback | Solo sch |
| ERC / DRC | Solo DRC (kicad-cli) | ERC+DRC (kicad-cli) | DRC (no vi ERC en registry) | ERC+DRC vía kicad-cli/gates | No |
| Exportación | Thumbnails, BOM CSV | Gerber (experimental) | 27 formatos (Gerber, IPC-2581, ODB++, PDF, STEP…) | Gerber/BOM/IPC-2581/STEP + gates | No |
| Mecanismo | kicad-cli + parsing S-expr | kicad-cli + SWIG + S-expr | SWIG (default) + IPC kipy opcional + kicad-cli | kipy (IPC) + kicad-sch-api + kicad-cli | kicad-sch-api (S-expr) |
| ¿Requiere KiCad abierto? | No | No (recomienda cerrarlo al editar) | No con SWIG; sí con IPC | Sí para funciones IPC; no para archivo/cli (INFERRED) | No |
| KiCad soportado | 9+ (README) | 8+, recomienda 9/10 (VERIFIED README) | 9 y 10 (VERIFIED README/changelog) | 9 y 10 (VERIFIED Dockerfiles/fork docs) | 9 (INFERRED) |
| Windows | Parcial: `open_project` NO soporta win32 (VERIFIED código) | Sí | Sí, "fully supported", setup-windows.ps1 (VERIFIED) | Sí, CI en windows-2025 (VERIFIED ci.yml) | Sin evidencia |
| cliente MCP | Compatible MCP genérico | Sí (trae archivo de instrucciones del cliente) | Soportado explícitamente (VERIFIED README) | Soportado explícitamente | Compatible genérico |
| Acceso a red | No | No | **Sí: jlcsearch.tscircuit.com + JLCPCB** (VERIFIED código) | Catálogo JLCPCB por defecto; Nexar/DigiKey/Mouser solo con credenciales (VERIFIED README) | No |
| Telemetría | No encontrada (VERIFIED grep) | No encontrada (VERIFIED grep) | No encontrada (VERIFIED grep) | **OFF por defecto**, OTel opt-in con scrubbing de secretos (VERIFIED código) | No encontrada |
| Riesgo destacado | Vulnerabilidad abierta sin respuesta (#57) | Edición corrompe render de símbolos en KiCad 10 (#9 abierto) | Corrupción sch en KiCad 10 en <2.3.0 (arreglada, VERIFIED changelog) | Proyecto de 5 semanas, 1 mantenedor, Python ≥3.13 | Estancado, alcance mínimo |

---

## 3. Fichas por candidato

### 3.1 lamaalrajih/kicad-mcp — DESCARTADO
- **Repo:** https://github.com/lamaalrajih/kicad-mcp · MIT · Python · 481★ (VERIFIED API GitHub).
- **Actividad:** último push 2025-10-17; ~15 PRs de la comunidad sin merge; efectivamente **abandonado ~9 meses** (VERIFIED API + issues; abandono es INFERRED).
- **Instalación:** clone + uv + `python main.py` (VERIFIED README).
- **Herramientas (VERIFIED código, 18, solo lectura/análisis):** `list_projects`, `get_project_structure`, `open_project`, `validate_project`, `analyze_bom`, `export_bom_csv`, `extract_schematic_netlist`, `extract_project_netlist`, `analyze_schematic_connections`, `find_component_connections`, `get_drc_history`, `run_drc_check`, `identify_circuit_patterns`, `analyze_project_circuit_patterns`, `generate_pcb_thumbnail`, `generate_project_thumbnail`, `validate_project_boundaries`, `generate_validation_report`. **No escribe archivos KiCad.**
- **Mecanismo:** `kicad-cli` por subprocess con validación (`secure_subprocess.py`) + parsing directo de S-expr (VERIFIED código).
- **Windows:** `open_kicad_project()` devuelve "Unsupported operating system" en win32 — solo macOS/Linux (VERIFIED `kicad_utils.py:88-122`). El resto funciona, pero el issue #24 de Windows tardó en resolverse.
- **Seguridad:** issue **#57 abierto y sin respuesta** (mayo 2026): la clase `PathValidator` existe pero **ningún tool la invoca** → enumeración de filesystem y oráculo de existencia de rutas vía `project_path` (VERIFIED issue). Sin red, sin telemetría.
- **Veredicto:** el más citado en listas awesome-mcp pero hoy es el peor candidato: sin mantenimiento + vulnerabilidad conocida sin parche.

### 3.2 Seeed-Studio/kicad-mcp-server — RECOMENDADO PARA LECTURA/VALIDACIÓN
- **Repo:** https://github.com/Seeed-Studio/kicad-mcp-server · Python · 58★ · creado 2026-01-25, último push 2026-05-22 (VERIFIED API). Mantenedor: organización Seeed Studio (fabricante real de hardware).
- **Licencia:** MIT declarada en `pyproject.toml` pero **falta el archivo LICENSE** (VERIFIED; GitHub no la detecta). Gap menor de compliance.
- **Instalación:** `pip install -e .` — recomendado dentro del Python embebido de KiCad (`C:\Program Files\KiCad\<ver>\bin\python.exe`) para tener `pcbnew`; fallback en Python del sistema con parsing de texto (VERIFIED README). Dependencia principal: `fastmcp`.
- **Herramientas (VERIFIED código, ~36):**
  - *Lectura sch:* `list_schematic_components`, `get_symbol_details`, `search_symbols`, `list_schematic_nets`, `get_schematic_info`, `search_components_by_type`.
  - *Netlist/jerarquía:* `generate_netlist`, `trace_netlist_connection`, `get_netlist_nets`, `get_netlist_components`, `trace_hierarchical_connection`, `analyze_hierarchical_nets`.
  - *PCB:* `list_pcb_footprints`, `get_pcb_statistics`, `analyze_pcb_nets`, `find_tracks_by_net`, `analyze_pcb_signal_integrity`, `analyze_pcb_power_integrity`.
  - *Validación:* `run_erc`, `run_drc`, `get_erc_violations`, `get_drc_violations`, `export_erc_report`, `export_drc_report` (todo vía `kicad-cli sch erc` / `pcb drc`, args fijos, sin shell=True — VERIFIED `validation.py:244-259`).
  - *Pines/codegen:* `analyze_pin_functions`, `detect_pin_conflicts`, `extract_pinmux_config`, `generate_device_tree`, `extract_gpio_config`, `extract_i2c_devices`, `extract_spi_devices`, `extract_power_domains`, `validate_pin_configuration`.
  - *Edición (EXPERIMENTAL):* `create_kicad_project`, `add_component_from_library`, `add_wire`, `add_label`, `setup_pcb_layout`, `export_gerber`.
- **Mecanismo:** kicad-cli + SWIG pcbnew + escritura directa de S-expr. No requiere KiCad abierto; recomienda cerrarlo al editar (VERIFIED README).
- **Estabilidad:** issues de lectura se corrigen rápido (#3,#4,#7 cerrados con PR). Escritura floja: **#9 abierto — en KiCad 10 los símbolos añadidos se renderizan mal** (caché lib_symbols vacío); sin mecanismo de backup en el editor (VERIFIED grep). Sin reportes de corrupción destructiva.
- **Seguridad:** sin red, sin telemetría, subprocess seguro. Riesgo bajo si se usa solo lectura+ERC/DRC.

### 3.3 mixelpixx/KiCAD-MCP-Server — RECOMENDADO COMO SUITE COMPLETA
- **Repo:** https://github.com/mixelpixx/KiCAD-MCP-Server · MIT · 1 454★ · 234 forks · v2.3.1 (6 jul 2026) · push el mismo día del informe → **el más activo del ecosistema** (VERIFIED API/releases).
- **Arquitectura:** servidor MCP en Node/TypeScript (`@modelcontextprotocol/sdk`) que lanza un proceso Python persistente (`kicad_interface.py`); backend dual **SWIG (default, headless) / IPC kipy (con GUI, sincronización en vivo)** con autodetección y variable `KICAD_BACKEND` (VERIFIED `factory.py`, `server.ts`).
- **Requisitos:** KiCad 9+, Node 18+, Python 3.9+ (usa el Python de KiCad para pcbnew). Windows 10/11 "fully supported" con `setup-windows.ps1`; cliente MCP listado como cliente soportado (VERIFIED README + scripts presentes).
- **Herramientas (VERIFIED `src/tools/registry.ts`):** ~25 directas (`create_project`, `open_project`, `save_project`, `snapshot_project`, `place_component`, `route_trace`, `sync_schematic_to_board`…) + ~92 enrutadas en 12 categorías: board (9), component (8), **export (27 formatos:** Gerber, drill, IPC-2581, ODB++, IPC-D-356, GenCAD, PDF, SVG, DXF, STEP/3D, VRML, BOM, netlist, pos), drc (8: `run_drc`, `get_drc_violations`, `check_clearance`, net classes), schematic (25: crear/editar/conectar/anotar/netlist), library (4), symbol_pins (2), hierarchy (2), layout (3), batch (6), routing (2), autoroute Freerouting (4, requiere Java/Docker opcional). No localicé un tool `run_erc` (VERIFIED registry; ERC ausente).
- **Protección de escritura (VERIFIED `kicad_interface.py`):** auto-save con **backups rotativos con timestamp en `.mcp-backups/` (conserva 20)**; `save_project` **rechaza sobrescribir ediciones externas** hechas fuera del MCP (#244→#289 cerrado).
- **Historial de corrupción (VERIFIED changelog + issues):** versiones <2.3.0 podían **corromper esquemáticos KiCad 10** (bloques de instancia incompletos: arrastrar un símbolo podía crashear KiCad; #220/#221/#256). v2.3.0 lo arregló con escritura "byte-equivalente a eeschema" según changelog (la afirmación byte-equivalente es UNVERIFIED). El proyecto es notablemente transparente documentando sus propios bugs.
- **Seguridad:** los `exec()` del lado TS solo validan el intérprete Python configurado (`--version`, `import pcbnew`), no exponen ejecución arbitraria vía tools (VERIFIED `server.ts:356-440`). **Acceso a red:** búsqueda de componentes contra `jlcsearch.tscircuit.com` (proxy de terceros, no JLCPCB directo) y descarga de footprints JLCPCB (VERIFIED `jlcsearch.py`, `jlcpcb_downloader.py`) → consultas de componentes salen a un servidor de terceros. Sin telemetría detectada (VERIFIED grep). Issue abierto #305 "Harden MCP request handling" (auto-auditoría con Codex). Superficie de ~120 tools = superficie de ataque/error grande.

### 3.4 oaslananka/kicad-mcp (paquete `kicad-mcp-pro`) — EMERGENTE, EN OBSERVACIÓN
- **Repo canónico:** https://github.com/oaslananka/kicad-mcp (el repo `oaslananka/kicad-mcp-pro` de las búsquedas devuelve 404; migrado desde el monorepo `kicad-studio-kit` — VERIFIED). PyPI/npm: `kicad-mcp-pro` v3.19.0 (5 jul 2026). MIT. **17★, creado 2026-05-31** (VERIFIED API).
- **Instalación:** `uvx kicad-mcp-pro` / pip / npx; app de escritorio Tauri para Windows; dashboard web en `127.0.0.1:3334` (VERIFIED README). **Requiere Python ≥3.13** (VERIFIED pyproject.toml) — tu 3.12.5 no sirve directo, aunque `uvx` puede aprovisionar 3.13 automáticamente (INFERRED, comportamiento estándar de uv).
- **Mecanismo:** `kicad-python` (kipy/IPC oficial) + `kicad-sch-api` (edición directa de .kicad_sch) + kicad-cli para validación/exportación (VERIFIED dependencias y grep de código).
- **Herramientas:** 38 módulos (VERIFIED listado `src/kicad_mcp/tools/`): schematic, pcb, routing, validation con **gates**, DFM, signal/power integrity, EMC, simulación SPICE, manufacturing/export, jobset, variants, visual_qa, signoff, version_control y **transacciones de esquemático**: `sch_plan/preview/apply/verify/rollback` sobre `transactional_write` atómico con checkpoint (VERIFIED `sch_transaction.py`). El README es honesto: SI/PI/EMC son "estimaciones de primer orden ~5-10%", no sign-off (VERIFIED README).
- **Postura de seguridad — la mejor del grupo (VERIFIED archivos):** telemetría OpenTelemetry **desactivada por defecto**, endpoints locales, scrubbing por regex de secretos/rutas/IPs (`utils/telemetry.py`); docs `threat-model.md`, `input-validation.md`; CodeQL, Gitleaks, Trivy, OpenSSF Scorecard, **OpenSSF Best Practices Silver**, firmas Sigstore; CI en Windows (windows-2025). Sourcing: catálogo público JLCPCB por defecto; Nexar/DigiKey/Mouser solo con credenciales explícitas.
- **Riesgos:** proyecto de ~5 semanas como repo independiente, comunidad casi nula (17★, 0 issues = también 0 validación externa), un solo mantenedor (INFERRED), superficie funcional enorme sin rodaje real, y procesos extra (dashboard HTTP, tray, GUI) que amplían superficie local. **No recomendable como base todavía; re-evaluar en 3-6 meses.**

### 3.5 circuit-synth/mcp-kicad-sch-api — DESCARTADO
- https://github.com/circuit-synth/mcp-kicad-sch-api · MIT · 20★ · último push 2025-08-20 (estancado, VERIFIED API). 28 tools solo de esquemático (`create/load/save_schematic`, `add_component`, `add_wire`, `backup_schematic`, bulk ops — VERIFIED `server.py`). Sin PCB, sin ERC/DRC. Su valor real es la librería subyacente `kicad-sch-api`, que oaslananka ya consume como dependencia.

### 3.6 Complementarios (datasheets/componentes)
- **Farad-Labs/nexar-mcp** (https://github.com/Farad-Labs/nexar-mcp): MIT, Python, v0.0.1 (dic 2025), 8★. Tools: `search_components`, `get_part_details`, `get_datasheet`, `search_bom`, `find_resistors/capacitors/inductors/semiconductors/crystals/connectors` (VERIFIED vía docs del repo). Requiere credenciales Nexar (API gratuita con límites); despliegue Docker con secrets, non-root, sin log de datos sensibles (UNVERIFIED — claims del README, código no auditado en profundidad). Tercero, no oficial de Nexar. Muy joven: usar solo con credenciales de cuenta desechable y revisión previa del código (~10 commits, auditable en minutos).
- Alternativa similar: `lukel99/octopart-mcp` (no auditado).
- Para documentación técnica general, el sourcing integrado de mixelpixx (JLCPCB) y de kicad-mcp-pro ya cubre parte del caso de uso sin añadir otro servidor.

---

## 4. Auditoría de seguridad transversal

1. **Ninguno sandboxea el filesystem.** Todos aceptan rutas arbitrarias y operan con los permisos del usuario (VERIFIED en los 3 principales; lamaalrajih tiene incluso un validador escrito pero muerto — issue #57). Mitigación: sandbox por convención (directorio de trabajo dedicado + git) y permisos de herramienta en cliente MCP (`permissions.deny`/`ask` para tools de escritura).
2. **Ejecución de comandos:** ninguno expone un tool de "ejecutar comando arbitrario". Los subprocess van a `kicad-cli`/Python con listas de args fijas, sin `shell=True` (VERIFIED lamaalrajih, Seeed, mixelpixx). El riesgo real es indirecto: rutas de intérprete configurables por env (`KICAD_PYTHON`) — quien controle el env del servidor controla qué binario se ejecuta (INFERRED).
3. **Red:** Seeed y lamaalrajih = cero red. mixelpixx llama a `jlcsearch.tscircuit.com` (tercero) y JLCPCB al usar tools de sourcing — tus búsquedas de componentes salen de tu máquina (VERIFIED). kicad-mcp-pro consulta el catálogo JLCPCB por defecto. Si eso incomoda: no invocar esas categorías o bloquear los dominios.
4. **Telemetría:** ninguna activa por defecto en ningún candidato (VERIFIED greps; en kicad-mcp-pro explícitamente opt-in con scrubbing).
5. **Escritura destructiva:** el peligro nº1 del ecosistema es la **corrupción de S-expressions**. Evidencia real: mixelpixx <2.3.0 corrompía sch en KiCad 10 (arreglado); Seeed #9 abierto (símbolos mal embebidos). Solo mixelpixx (backups rotativos + no-clobber) y kicad-mcp-pro (transacciones+rollback) tienen defensas nativas. **Git es obligatorio como red de seguridad externa en todos los casos.**
6. **Concurrencia con la GUI:** editar archivos mientras KiCad los tiene abiertos puede perder cambios de un lado u otro. Regla: KiCad cerrado durante escrituras por archivo (Seeed/mixelpixx-SWIG), o backend IPC con GUI abierta (mixelpixx-IPC) pero nunca ambos a la vez.

---

## 5. Recomendación final

**Versión de KiCad a instalar: KiCad 10.0.x estable** (ambos finalistas lo soportan explícitamente; kicad-cli más completo; IPC más maduro; formato sch 20260101 ya manejado por mixelpixx 2.3.x — VERIFIED). Alternativa conservadora: 9.0.x último minor. Evitar nightlies de KiCad 11.

### Top 2

**#1 — mixelpixx/KiCAD-MCP-Server v2.3.1** (suite completa: lectura + escritura + DRC + exportación + autoroute)
Justificación: único con mantenimiento diario, comunidad real (1.4k★), Windows first-class, cliente MCP soportado, backups automáticos y protección no-clobber. Sus bugs de escritura existieron pero se corrigen rápido y con transparencia.

**#2 — Seeed-Studio/kicad-mcp-server** (capa de lectura/validación de bajo riesgo)
Justificación: superficie pequeña y legible, ERC+DRC vía kicad-cli (que a mixelpixx le falta el ERC), cero red, mantenedor corporativo. Usar SOLO sus tools de lectura/validación; su edición experimental se desactiva/ignora.

*En observación:* `kicad-mcp-pro` (oaslananka) — mejor ingeniería de seguridad del grupo (transacciones con rollback, OpenSSF Silver, telemetría opt-in), pero 17★, 5 semanas de vida, un mantenedor y Python ≥3.13. Re-evaluar en el Q4 2026; si madura, es el candidato natural para sustituir a #1 en escritura.

### Plan de instalación en modo controlado

**Fase 0 — Base (sin MCP):**
1. Instalar KiCad 10.0.x estable; verificar `kicad-cli version` y `"C:\Program Files\KiCad\10.0\bin\python.exe" -c "import pcbnew"`.
2. Crear proyecto desechable `C:\PCBMCP\sandbox\demo` con `git init` + commit inicial. Nada del MCP toca proyectos reales hasta la Fase 3.

**Fase 1 — Solo lectura (Seeed):**
3. Instalar Seeed en el Python embebido de KiCad (`pip install -e .` según su README) y registrarlo en `.mcp.json` del proyecto (scope proyecto, transporte stdio).
4. En la configuración local del cliente MCP, restringir herramientas de escritura usando los mecanismos de permisos disponibles para `add_component_from_library`, `add_wire`, `add_label`, `setup_pcb_layout`, `create_kicad_project` (sus tools de escritura).
5. Probar sobre un proyecto de ejemplo de KiCad: `get_schematic_info` → `list_schematic_nets` → `run_erc` → `run_drc`. Criterio de éxito: resultados coherentes con la GUI y cero modificaciones (verificar `git status` limpio).

**Fase 2 — Escritura en sandbox (mixelpixx):**
6. Clonar tag v2.3.1 (pin de versión, no `main`), `npm install && npm run build`, ejecutar `setup-windows.ps1` revisándolo antes.
7. Registrar en `.mcp.json` con `KICAD_BACKEND=swig` (headless, KiCad cerrado). `permissions.ask` para toda tool de escritura/exportación.
8. Ciclo de prueba en `sandbox\demo`: crear proyecto → añadir 3-4 componentes → conectar → `run_drc` → `export_gerber`. Tras cada lote: `git diff` para inspeccionar qué escribió, abrir en KiCad GUI y comprobar que carga sin warnings, mover un símbolo (test de corrupción de instancias), cerrar sin guardar.
9. Verificar que `.mcp-backups/` se puebla y ensayar una restauración.
10. No usar tools de sourcing JLCPCB si no se acepta la salida de red a `jlcsearch.tscircuit.com`.

**Fase 3 — Adopción gradual:**
11. Solo tras ≥2 sesiones de Fase 2 sin anomalías, permitir escritura en proyectos reales, siempre bajo git y con commit previo a cada sesión de agente.
12. Opcional: añadir `nexar-mcp` para datasheets (credenciales Nexar en cuenta dedicada; leer su código antes — son ~10 commits).

---

## 6. Fuentes principales
- Repos y API GitHub (metadata, issues, código clonado 2026-07-06): lamaalrajih/kicad-mcp · Seeed-Studio/kicad-mcp-server · mixelpixx/KiCAD-MCP-Server · oaslananka/kicad-mcp · circuit-synth/mcp-kicad-sch-api · Farad-Labs/nexar-mcp
- Issues clave: lamaalrajih#57 (vulnerabilidad path validation), Seeed#9 (KiCad 10), mixelpixx#220/#221/#244/#256/#289 (corrupción/clobber, cerrados)
- Docs oficiales KiCad: dev-docs.kicad.org (IPC API, SWIG deprecation), docs.kicad.org/kicad-python-main (kipy: GUI requerida en 9/10, headless en 11)
