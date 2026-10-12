# Informe de estado inicial del entorno

**Fecha:** 2026-07-06
**Máquina:** Windows 11 Home 10.0.26200 (x64)
**Workspace:** `C:\PCBMCP` (vacío al inicio, git inicializado el 2026-07-06)

## Hardware

| Recurso | Valor | Estado |
|---|---|---|
| RAM total | 15.3 GB | VERIFIED (`Win32_OperatingSystem`) |
| RAM libre al inspeccionar | ~0.5 GB | VERIFIED — ⚠️ riesgo: poca RAM libre; evitar correr KiCad GUI + Docker + muchos agentes a la vez |

## Herramientas presentes (VERIFIED por ejecución)

| Herramienta | Versión | Ruta |
|---|---|---|
| Python | 3.12.5 | `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` |
| pip | presente | ídem `\Scripts\pip.exe` |
| uv | 0.11.25 | `%USERPROFILE%\.local\bin\uv.exe` |
| Node.js | 22.20.0 | `C:\Program Files\nodejs\` |
| Git | 2.54.0.windows.1 | `C:\Program Files\Git\` |
| Java | 21.0.9 LTS (Oracle) | javapath — suficiente para FreeRouting (requiere Java moderno) |
| Docker | 29.2.0 | Docker Desktop |
| winget | 1.29.280 | — |

## Herramientas EDA ausentes (VERIFIED por búsqueda en PATH y Program Files)

- **KiCad**: no instalado. winget ofrece `KiCad.KiCad` **10.0.3** (VERIFIED vía `winget search`).
- **ngspice** standalone: no instalado y **no disponible en winget** (VERIFIED). KiCad incluye ngspice embebido para su simulador; instalación standalone requiere descarga manual — pendiente de decisión.
- **FreeRouting**: no instalado. Java 21 disponible como prerequisito.
- No hay LTspice ni otras herramientas EDA en `Program Files`.

## Python: paquetes EDA

Sin paquetes EDA previos (no hay skidl, kiutils, kicad-*). Presente `click 8.4.2` en el Python global.
**Decisión:** todo lo del proyecto irá en un venv propio (uv) para no tocar el Python global.

## Integraciones de desarrollo y MCP

- El inventario inicial no identificó servidores MCP globales de EDA. La configuración local del proyecto se mantuvo separada de las preferencias globales del equipo.
- Las tareas de revisión y automatización deben tener instrucciones reproducibles, evidencia de ejecución y límites explícitos para cualquier herramienta con capacidad de escritura.
- Los perfiles de responsabilidad técnica están en `docs/engineering_roles.md`.

## Riesgos identificados

1. **RAM libre baja (~0.5 GB al medir):** cerrar aplicaciones pesadas antes de correr KiCad + agentes; preferir `kicad-cli` headless sobre GUI.
2. **ngspice standalone no está en winget:** verificar si el ngspice embebido de KiCad 10 sirve para automatización batch o si hay que instalar el paquete oficial manualmente.
3. **Sin instalaciones previas de KiCad:** ventaja (sin conflictos de versión), pero todo el stack debe validarse desde cero.
