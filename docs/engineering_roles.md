# Responsabilidades técnicas para el pipeline EDA

Este documento recoge funciones de ingeniería y criterios de aceptación independientes de un proveedor de asistencia. Las decisiones de diseño y los resultados de pruebas deben estar respaldados por fuentes y ejecuciones verificables.

## Criterios comunes

- Distinguir `VERIFIED`, `TESTED`, `INFERRED`, `UNVERIFIED` y `BLOCKED` según la evidencia realmente disponible.
- No inventar pinouts, características eléctricas, compatibilidad de archivos ni resultados de pruebas.
- Priorizar API y CLI oficiales; utilizar herramientas comunitarias solo después de revisar sus riesgos.
- No sobrescribir trabajo manual en KiCad. Mantener respaldo, verificación de integridad y un único escritor activo.
- No fabricar una placa sin revisar esquema, PCB, ERC, DRC, BOM y paquete final.

## Áreas de responsabilidad

### Arquitectura EDA
Define fuentes de verdad por fase, puntos de transferencia de autoridad, alternativas, riesgos y pruebas de validación. Documenta las decisiones en `docs/architecture.md` y los ADR.

### Selección de componentes
Documenta MPN, fabricante, encapsulado, footprint, fuente primaria, evidencias, riesgos y alternativas en `bom/component_candidates.csv`. Registra hechos confirmados en `knowledge/datasheet_facts/` y verifica obsolescencia, compatibilidad y disponibilidad.

### Automatización KiCad
Comprueba experimentalmente las capacidades de la versión instalada. Da prioridad a API/CLI oficiales; valida parseo de proyectos y conserva reportes ERC/DRC en `reports/`.

### Generación de esquemáticos
Separa intención, bloques, selección de componentes, conectividad y presentación. Verifica redes de alimentación, símbolos y pines con datasheets; exige que KiCad abra el resultado.

### Simulación
Clasifica el nivel de fidelidad de cada modelo SPICE, ejecuta análisis reproducibles y conserva netlists, parámetros, salidas, interpretación y limitaciones.

### Diseño físico de PCB
Clasifica redes críticas, planifica placement, retorno de corriente, EMI, disipación y reglas físicas. Enruta manualmente señales sensibles; cualquier automatización requiere DRC posterior.

### Validación ERC/DRC
Ejecuta verificaciones reales, clasifica cada hallazgo con evidencia y no silencia errores para forzar reportes satisfactorios. Audita también footprints, BOM, planos, nets y archivos exportados.

### Revisión adversarial de hardware
Examina protección de entrada, arranque, reset, alimentación, niveles lógicos, desacoplo, térmica, retornos, footprints, conectores y facilidad de prueba. Registra severidad, evidencia y corrección mínima en `reviews/`.

### Seguridad de integraciones
Evalúa código fuente, licencia, mantenimiento, privilegios de lectura/escritura/ejecución, telemetría, compatibilidad con Windows y límites de acceso antes de incorporar dependencias o servidores MCP.

### Fabricación y DFM
Valida Gerbers, Excellon, BOM, pick-and-place, contorno, stackup, tolerancias y reglas documentadas del fabricante. Comprueba consistencia entre PCB, BOM y archivos de ensamblaje.

### Integración y pruebas
Mantiene `uv.lock`, herramientas reproducibles, CLI `pcb-ai`, códigos de salida, respaldos y pruebas unitarias, de integración y de humo. Los comandos deben funcionar en PowerShell o tener una alternativa documentada. Nunca afirma que un test pasó sin ejecutarlo.
