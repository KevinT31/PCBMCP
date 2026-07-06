# Stack de automatización KiCad — Estado a julio 2026

> Investigación para el pipeline agéntico requisitos → esquemático → ERC → simulación → PCB → DRC → fabricación.
> Etiquetas: **VERIFIED** (fuente oficial consultada), **INFERRED** (deducción razonable de evidencia), **UNVERIFIED** (requiere prueba local o confirmación).
> Máquina objetivo: Windows 11 Home x64, 16 GB RAM, Python 3.12.5, Node 22, Java 21, uv, winget 1.29.

---

## 1. KiCad: versión estable actual

| Dato | Valor | Estado |
|---|---|---|
| Versión estable | **KiCad 10.0.4** (21-jun-2026) | VERIFIED |
| Primera 10.x estable | 10.0.0 (20-mar-2026) | VERIFIED |
| ID winget | `KiCad.KiCad` (winget sirve **10.0.3**, 20-may-2026; va ~1 versión por detrás) | VERIFIED (consultado con `winget show` local) |
| Tipo de instalador | NSIS (nullsoft) → silencioso nativo con `/S`; winget usa `--silent` | VERIFIED |
| Tamaño descarga Win x64 | ~967 MB (`kicad-10.0.4-x86_64.exe`, 966.785.896 bytes vía API GitHub) | VERIFIED |
| Tamaño instalado | ~6–9 GB (bibliotecas de símbolos/huellas + modelos 3D) | INFERRED |

- Anuncio 10.0.0: https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/
- 10.0.4: https://www.kicad.org/blog/2026/06/KiCad-10.0.4-Release/
- Instalador: https://github.com/KiCad/kicad-source-mirror/releases/tag/10.0.4

Novedades 10.0 relevantes para automatización: variantes de diseño (flag `--variant` en kicad-cli), editor gráfico de reglas DRC, importadores Allegro/PADS/gEDA. **VERIFIED** (blog oficial).

KiCad publica una major al año: v9 (2025) → v10 (2026). KiCad 11 está en desarrollo (master). **VERIFIED**.

---

## 2. kicad-cli 10.0 (doc oficial: https://docs.kicad.org/10.0/en/cli/cli.html)

Comandos top-level: `fp`, `sym`, `sch`, `pcb`, `jobset`, `version`. **VERIFIED**.

### `sch` (esquemático)
| Subcomando | Notas |
|---|---|
| `erc` | Formatos de salida: **`report` o `json`**; `--exit-code-violations` para CI |
| `export pdf / svg / dxf / ps` | Gráficos (`hpgl` no funcional en 10.0) |
| `export bom` | BOM con presets y formatos configurables |
| `export netlist` | Formatos: `kicadsexpr`, `kicadxml`, `cadstar`, `orcadpcb2`, **`spice`**, `spicemodel`, `pads`, `allegro` |
| `export python-bom` | Flujo BOM legado (XML) |
| `upgrade` | Convierte .kicad_sch antiguos al formato actual |

### `pcb`
| Subcomando | Notas |
|---|---|
| `drc` | Formatos: **`report` o `json`**; `--schematic-parity`; `--exit-code-violations` |
| `export gerbers / drill / pos / ipc2581 / ipcd356 / odb` | Fabricación completa (Gerber X2, Excellon, IPC-2581 B/C, ODB++) |
| `export pdf / svg / dxf / ps / gencad` | Documentación/CAD |
| `export step / stl / glb / brep / ply / stpz / u3d / vrml / xao / 3dpdf` | 3D |
| `render` | PNG/JPEG raytraced con cámara/iluminación configurables |
| `export stats` | Estadísticas de placa en `report` o `json` |
| `import` | Importa altium, eagle, pads, cadstar, fabmaster, pcad, solidworks |
| `upgrade` | Actualiza formato de placa |

### Otros
- `jobset run`: ejecuta conjuntos de trabajos predefinidos (.kicad_jobset) — ideal para pipelines reproducibles. **VERIFIED**.
- Soporte de variables (`--define-var`) y variantes (`--variant`). **VERIFIED**.

**Huecos importantes:**
- **NO hay comando de simulación** en kicad-cli (el simulador integrado es solo GUI). **VERIFIED** (ausente de la doc CLI 10.0).
- **NO hay export Specctra DSN ni import SES** en kicad-cli 10.0. **VERIFIED** (ausente de la doc; ver §6 para alternativas).
- Headless en Windows: kicad-cli está diseñado para CI (JSON + exit codes) y no abre GUI. **VERIFIED** el diseño; el comportamiento real en esta máquina Windows (p.ej. `pcb render` sin GPU dedicada) → **UNVERIFIED, probar localmente**.

---

## 3. IPC API oficial y bindings Python

| Aspecto | Estado | Etiqueta |
|---|---|---|
| API oficial | IPC API: Protobuf + NNG sobre socket/pipe local (Win/mac/Linux) | VERIFIED |
| Paquete Python oficial | `kicad-python` (import `kipy`), **v0.7.1** (17-abr-2026), Python ≥3.9, deps `protobuf` + `pynng` | VERIFIED |
| Requisito | **Exige KiCad en ejecución** con el servidor API habilitado en Preferencias; "It is not possible to use kicad-python to manipulate KiCad design files without KiCad running" | VERIFIED (PyPI) |
| Cobertura en KiCad 9/10 | **Solo editor de PCB**. "In KiCad 9.0, the IPC API… only implemented in the PCB editor". Esquemático/editores de librería: futuro | VERIFIED |
| Variables de entorno | `KICAD_API_SOCKET` y `KICAD_API_TOKEN` (inyectadas al lanzar plugins; un cliente externo puede descubrir el socket con una sola instancia abierta) | VERIFIED |
| SWIG pcbnew | **Deprecado desde 9.0**; sigue presente en 9 y 10; "The current plan is to remove the SWIG bindings in KiCad 11.0" | VERIFIED |
| API headless vía kicad-cli | dev-docs (master) sugiere que llega **en KiCad 11**, no en 10 | UNVERIFIED (doc de master, re-verificar) |

- IPC API: https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/
- SWIG: https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/index.html
- kipy: https://pypi.org/project/kicad-python/ · docs: https://docs.kicad.org/kicad-python-main/

**Implicación para el pipeline:** la IPC API sirve para manipulación interactiva de PCB (con GUI abierta), no para batch headless ni para esquemáticos. Para scripting headless de PCB en KiCad 10 aún se puede usar el Python SWIG embebido de KiCad (`pcbnew`), sabiendo que muere en v11. **INFERRED**.

---

## 4. Automatización de ESQUEMÁTICOS (.kicad_sch)

No existe vía oficial de escritura programática de esquemáticos en KiCad 10 (ni CLI ni IPC API). Opciones de terceros:

| Herramienta | Última actividad | Compat. formato | Riesgos | Veredicto |
|---|---|---|---|---|
| **kicad-sch-api** (circuit-synth) | v0.5.6 (19-nov-2025); repo actualizado dic-2025 | Declara KiCad **7/8** con preservación de formato byte-a-byte; 9/10 no declarado | Formato 9/10 no garantizado | **Candidato principal**, validar con v10 |
| **kicad-skip** (psychogenic) | v0.2.5 (feb-2024), último commit abr-2024 | Parser S-expr genérico; probado con formato ~v7/v8 | **Sin mantenimiento 2+ años**; 22 issues abiertos | Fallback utilizable con validación |
| **kiutils** (mvnmgrx) | v1.4.8 (feb-2024) | "KiCad 6.0 and up" (en la práctica ≤7/8 parcial) | **Estancado 2,5 años**; dataclasses rígidas rompen con campos nuevos de 9/10 | Evitar para v10 (INFERRED) |
| **S-expressions directas** (sexpdata / plantillas) | n/a | Total (tú controlas el formato) | Coste de desarrollo; hay que replicar UUIDs, `lib_symbols`, instancias | Base sólida para casos simples |
| **circuit-synth** | repo actualizado mar-2026; v0.12.x | Python→KiCad y KiCad→Python bidireccional; optimizado para Claude Code; incluye MCP `mcp-kicad-sch-api` | Proyecto joven, un mantenedor principal | **Muy relevante** para pipeline agéntico |

- kicad-sch-api: https://pypi.org/project/kicad-sch-api/ · https://github.com/circuit-synth/kicad-sch-api
- kicad-skip: https://github.com/psychogenic/kicad-skip
- kiutils: https://github.com/mvnmgrx/kiutils
- circuit-synth: https://github.com/circuit-synth/circuit-synth · MCP: https://github.com/circuit-synth/mcp-kicad-sch-api

**Mitigación clave contra corrupción (INFERRED, diseñar así el pipeline):**
1. Generar/modificar .kicad_sch con la librería elegida.
2. Pasar `kicad-cli sch upgrade` para normalizar al formato 10.0.
3. Validar con `kicad-cli sch erc --format json --exit-code-violations` (si el parser de KiCad lo abre y el ERC corre, el archivo es estructuralmente válido).
4. Exportar PDF/SVG para revisión visual humana/LLM.

---

## 5. SKiDL

| Aspecto | Dato | Etiqueta |
|---|---|---|
| Versión | **2.2.3** (8-abr-2026) — mantenimiento activo (1.6k stars, 2154 commits) | VERIFIED |
| Compat. KiCad | Identificadores hasta **KICAD9**; README: "SKiDL supports KiCad 5 through 9". KiCad 10 aún no declarado | VERIFIED (v10: UNVERIFIED) |
| Netlist | Salida principal y madura (formato KiCad s-expr) → se importa en pcbnew | VERIFIED |
| ERC propio | Sí: pines sin conectar, conflictos de drive, errores de alimentación; `erc_assert()` para reglas custom | VERIFIED |
| Generación .kicad_sch | Contradicción en docs: changelog 2.2.2 dice "Schematic generation added for KiCad 6, 7, 8 and 9"; README dice "KiCad schematic files (currently V5 only)". Calidad/placement autogenerado históricamente experimental | UNVERIFIED — probar localmente |
| Riesgo | **Desincronización**: SKiDL es fuente de verdad paralela; el flujo natural es SKiDL→netlist→PCB, saltándose el .kicad_sch como fuente | INFERRED |

- https://pypi.org/project/skidl/ · https://github.com/devbisme/skidl

**Implicación:** SKiDL es la vía más robusta para *lógica de circuito* (conectividad + ERC temprano en Python puro), pero débil como generador de esquemático visual editable. Si KiCad debe ser source of truth, SKiDL encaja como generador inicial, no como editor iterativo. **INFERRED**.

---

## 6. FreeRouting

| Aspecto | Dato | Etiqueta |
|---|---|---|
| Release actual | **v2.2.4** (13-may-2026, `published_at` API GitHub) | VERIFIED |
| Java | **Java 25** (build.gradle: `JavaVersion.VERSION_25`; README recomienda Temurin 25). **El Java 21 instalado NO basta** | VERIFIED |
| CLI headless | Clásico vigente: `java -jar freerouting-2.2.4.jar -de placa.dsn -do placa.ses` (+ `-inc` para excluir netclasses) | VERIFIED |
| API REST | Beta desde 2.2.0: `--gui.enabled=false --api_server.enabled=true`, OpenAPI/Swagger, auth activada por defecto; también API cloud `api.freerouting.app/v1` y **integración MCP** | VERIFIED |
| Flujo con KiCad | KiCad GUI: File→Export→Specctra DSN → freerouting → File→Import→Specctra SES. **kicad-cli 10 no exporta DSN**; headless: funciones SWIG `pcbnew.ExportSpecctraDSN()` / `ImportSpecctraSES()` | DSN/SES por GUI: VERIFIED · vía SWIG headless: INFERRED, probar |
| Riesgos | Autoruteo de calidad variable (revisar siempre con DRC después); API beta "may change"; dependencia de SWIG para el paso headless desaparece en KiCad 11 | INFERRED |

- https://github.com/freerouting/freerouting · https://github.com/freerouting/freerouting/releases
- Issue integración kicad-cli DRC: https://github.com/freerouting/freerouting/issues/574

winget: **no existe paquete freerouting** (verificado con `winget search`). Instalar JAR desde GitHub Releases. **VERIFIED**.

---

## 7. ngspice y simulación en Windows

| Aspecto | Dato | Etiqueta |
|---|---|---|
| Versión actual | **ngspice 46** (29-mar-2026) | VERIFIED |
| winget | **No disponible** (verificado con `winget search ngspice`) | VERIFIED |
| Opciones Windows | 1) 7z portable oficial: `ngspice-46_64.7z` (GUI+consola, XSPICE, OpenMP) desde SourceForge; 2) Chocolatey `ngspice 46.0.0`; 3) DLL compartida `ngspice-46_dll_64.7z` | VERIFIED |
| Bundled con KiCad | Sí: KiCad embebe libngspice para su simulador interno (10.0.2 incluyó workaround para cambios de ngspice 46) — pero es la **DLL**, no el ejecutable CLI | VERIFIED |
| Simulador integrado KiCad | **Solo GUI** (Schematic Editor → Simulator). Sin acceso por kicad-cli | VERIFIED |
| Automatización batch | `kicad-cli sch export netlist --format spice circuito.kicad_sch` → `ngspice -b circuito.cir -o salida.log` (modo batch con `.control`/`wrdata` para extraer datos) | Netlist spice: VERIFIED · calidad del netlist exportado (modelos, directivas .sim): UNVERIFIED, probar |

- https://ngspice.sourceforge.io/download.html · https://community.chocolatey.org/packages/ngspice
- https://www.kicad.org/discover/spice/

**Implicación:** el pipeline de simulación agéntico = kicad-cli (netlist spice) + ngspice standalone en batch. El simulador interno de KiCad queda solo para inspección humana. **INFERRED**.

---

## 8. Herramientas emergentes (generación programática de esquemático/PCB)

| Herramienta | Versión / actividad | Qué hace | Compat. KiCad | Madurez |
|---|---|---|---|---|
| **atopile** | v0.15.7 (23-abr-2026), releases semanales; **requiere Python ≥3.14,<3.15** (¡no corre en el 3.12.5 instalado; uv puede instalar 3.14!) | Lenguaje declarativo `.ato` → compila y **actualiza .kicad_pcb nativo**; picking paramétrico de componentes; ecuaciones de diseño | Nativa (KiCad para layout, opcional para compilar) | Pre-1.0, muy activo, VS Code ext, VERIFIED |
| **tscircuit** | Muy activo 2026 (demos con agentes IA en mayo-2026) | Circuitos en React/TypeScript → PCB, esquemático, Gerbers, **KiCad, DSN**, netlists; import/export KiCad; librerías instalables vía KiCad PCM | Import y export KiCad + DSN | Activo; autorouting/DRC aún en desarrollo, VERIFIED |
| **circuit-synth** | v0.12.x, actualizado mar-2026 | Circuitos en Python ↔ KiCad bidireccional; **diseñado explícitamente para Claude Code** (agentes, BOM, FMEA); publica kicad-sch-api y su MCP | .kicad_sch real (7/8 declarado) | Joven, un equipo pequeño, VERIFIED |
| **FreeRouting MCP** | En README oficial 2026 | Integración MCP para agentes IA | vía DSN/SES | Beta, VERIFIED |

- https://atopile.io/ · https://pypi.org/project/atopile/
- https://tscircuit.com/ · https://blog.tscircuit.com/p/kicad-integration-parsing-and-exporting
- https://circuit-synth.readthedocs.io/

**Lectura estratégica (INFERRED):** el ecosistema 2025-2026 converge hacia "hardware como código + agentes IA" (atopile, tscircuit, circuit-synth). Ninguno reemplaza aún a KiCad como source of truth de nivel profesional, pero circuit-synth/kicad-sch-api es el único que trabaja directamente sobre .kicad_sch, que es lo que exige este proyecto.

---

## 9. Riesgos y huecos que requieren pruebas locales

1. **kicad-sch-api vs formato KiCad 10**: declara 7/8. Probar: generar sch → `kicad-cli sch upgrade` → `sch erc` → abrir en GUI. (UNVERIFIED)
2. **Roundtrip sin pérdida**: modificar un .kicad_sch creado por KiCad 10 con kicad-sch-api/kicad-skip y verificar diff limpio. (UNVERIFIED)
3. **SKiDL con librerías de símbolos KiCad 10** (identificador KICAD9 contra libs v10) y calidad real de su generación de .kicad_sch. (UNVERIFIED)
4. **Export DSN headless** con `pcbnew` SWIG del Python embebido de KiCad 10 en Windows. (INFERRED, sin probar)
5. **kicad-cli render 3D headless** en esta máquina (¿necesita OpenGL?). (UNVERIFIED)
6. **Netlist spice de kicad-cli**: ¿incluye modelos y directivas de simulación asignadas en el esquemático? (UNVERIFIED)
7. **Convivencia Java 21 / Java 25**: instalar Temurin 25 sin romper herramientas que dependan de 21 (usar JAVA_HOME por invocación, no global). (INFERRED)
8. **Fragilidad a futuro**: SWIG desaparece en KiCad 11; IPC API cubrirá esquemático y headless recién en v11 → re-evaluar el stack cuando salga 11.0 (≈marzo 2027). (INFERRED)

---

## 10. Plan de instalación recomendado para Windows

Orden recomendado (todo silencioso/scriptable):

```powershell
# 1. KiCad 10.0.x (winget sirve 10.0.3; NSIS silencioso). ~967 MB descarga, reservar ~10 GB disco
winget install --id KiCad.KiCad --silent --accept-package-agreements --accept-source-agreements
#    Alternativa para 10.0.4 exacto (mismo instalador NSIS):
#    Invoke-WebRequest https://github.com/KiCad/kicad-source-mirror/releases/download/10.0.4/kicad-10.0.4-x86_64.exe -OutFile kicad.exe
#    .\kicad.exe /S

# 2. Añadir kicad-cli al PATH de sesión (ruta típica; verificar tras instalar)
$env:Path += ";C:\Program Files\KiCad\10.0\bin"
kicad-cli version

# 3. Java 25 (Temurin) SOLO para FreeRouting — no tocar JAVA_HOME global (ya hay Java 21)
winget install --id EclipseAdoptium.Temurin.25.JRE --silent

# 4. FreeRouting 2.2.4 (no está en winget; JAR desde GitHub Releases)
New-Item -ItemType Directory -Force C:\Tools\freerouting
Invoke-WebRequest https://github.com/freerouting/freerouting/releases/download/v2.2.4/freerouting-2.2.4.jar -OutFile C:\Tools\freerouting\freerouting-2.2.4.jar
# Uso: & "C:\Program Files\Eclipse Adoptium\jre-25*\bin\java.exe" -jar C:\Tools\freerouting\freerouting-2.2.4.jar -de in.dsn -do out.ses

# 5. ngspice 46 (no está en winget; 7z portable oficial)
Invoke-WebRequest "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/46/ngspice-46_64.7z/download" -OutFile ngspice46.7z -UserAgent "Wget"
# Descomprimir en C:\Tools\ngspice y añadir C:\Tools\ngspice\Spice64\bin al PATH
# (alternativa: choco install ngspice)

# 6. Entorno Python del pipeline (uv, aislado del 3.12.5 del sistema)
uv init pcb-pipeline; cd pcb-pipeline
uv add kicad-python        # kipy 0.7.x — IPC API (PCB, requiere KiCad abierto)
uv add kicad-sch-api       # 0.5.x — manipulación .kicad_sch (validar contra v10)
uv add skidl               # 2.2.3 — netlist + ERC en Python
uv add sexpdata            # fallback S-expressions crudas

# 7. (Opcional, evaluación) atopile exige Python 3.14:
#    uv tool install --python 3.14 atopile
```

**Orden de validación post-instalación** (smoke tests que cierran los UNVERIFIED de §9):
1. `kicad-cli version` y `kicad-cli sch erc --format json` sobre un proyecto demo de KiCad.
2. Roundtrip kicad-sch-api sobre un .kicad_sch v10 + `sch upgrade` + ERC.
3. `"C:\Program Files\KiCad\10.0\bin\python.exe" -c "import pcbnew; print(pcbnew.Version())"` y prueba de `ExportSpecctraDSN`.
4. FreeRouting CLI con un DSN de ejemplo.
5. `kicad-cli sch export netlist --format spice` + `ngspice -b`.
