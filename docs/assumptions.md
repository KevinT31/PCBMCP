# Supuestos — demo-vigia rev A

Cada supuesto indica su impacto si resulta falso.

| ID | Supuesto | Impacto si es falso |
|---|---|---|
| S-1 | La placa se alimenta solo de puertos/cargadores USB estándar (5 V ± 10 %, ≥ 500 mA disponibles con pull-downs CC) | Redimensionar protección y presupuesto de corriente |
| S-2 | No se necesita comunicación de datos USB (el MCU no expone USB device) | Cambiar de MCU a uno con USB FS y añadir ESD en D+/D− (nueva revisión de spec) |
| S-3 | Consumo total del sistema ≤ 300 mA en +3V3 (MCU + sensor + LED ≪ 100 mA típico) | Revisar disipación del LDO y su package |
| S-4 | Entorno de operación 0–50 °C, sin requisitos industriales/automotrices | Re-seleccionar componentes por rango de temperatura |
| S-5 | El firmware no es entregable del demostrador; basta que el hardware sea programable y los buses accesibles | — |
| S-6 | JLCPCB acepta las reglas de la spec (0.2 mm traza/clearance, 0.3 mm drill) sin coste extra | Ajustar `manufacturing` en la spec (son reglas conservadoras, riesgo bajo) |
| S-7 | Las librerías oficiales de KiCad 10 tienen símbolo y footprint correctos para los componentes elegidos (curadas por el proyecto KiCad) | Fallback: símbolo/footprint local en `library/` del proyecto con revisión manual contra datasheet |
| S-8 | Un único puerto USB-C es suficiente (sin alimentación alternativa ni batería) | Nueva revisión de spec con ORing/protección adicional |
