# PCBMCP

Prototipo de automatización EDA para la placa **demo-vigia rev A**. Parte de una especificación YAML y genera un proyecto KiCad con comprobación eléctrica (ERC).

## Inicio rápido

Requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) y KiCad 10 para generar y verificar el esquema.

```powershell
uv sync --dev
uv run pcb-ai spec validate
uv run pcb-ai doctor --no-write
uv run pytest -q
uv run pcb-ai generate
uv run pcb-ai run-erc
```

El esquema actual está en `hardware/demo-vigia/`. El generador protege los archivos existentes mediante `build/emitted.sha256`; para volver a emitir este esquema desde una copia nueva, primero hay que revisar el artefacto y su historial. No uses `--force` sobre ediciones manuales que quieras conservar.

## Estado

- La especificación, el modelo y las pruebas automatizadas están disponibles.
- El ERC del esquema entregado tiene **cero infracciones** con KiCad 10. El modelo usa el símbolo base `Sensor_Temperature:LM75C` para el componente `LM75BD`, ya que `LM75B` es un alias que el generador no embebe de forma idéntica a la biblioteca.
- El PCB, la simulación completa y el paquete de fabricación aún no están implementados. No fabricar desde este repositorio sin completar esas etapas.

La arquitectura y las decisiones de componentes están en `docs/`; las pruebas de humo y los reportes están en `reports/`.
