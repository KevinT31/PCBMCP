# LM75BD,118 (NXP) — hechos de datasheet

Fuente primaria: "LM75B — Digital temperature sensor and thermal watchdog", Product data sheet
Rev. 6.1 — 6 febrero 2015 — NXP Semiconductors.
URL oficial: https://www.nxp.com/docs/en/data-sheet/LM75B.pdf (PDF descargado y leído).

## Identidad y package
- Orderable: **LM75BD,118** = package SO8 (SOT96-1, body 3.9 mm), reel 13". [DS p.3, Table 1/2] — VERIFIED
- AMBIGÜEDAD de nombre: Texas Instruments también vende un "LM75B" distinto. Este diseño usa el
  **NXP LM75BD**; especificar fabricante en el BOM. — VERIFIED (existencia de ambos catálogos)
- LCSC 2026-07-07: C34565 stock 3115, 0.6414 USD q5. API LCSC. — VERIFIED

## Alimentación
- VCC = 2.8–5.5 V (funciona a 3.3 V). [DS p.1, Features] — VERIFIED
- Desacoplo: el datasheet no impone valor; se aplica 100 nF estándar en VCC. — INFERRED

## Pinout SO8 [DS p.4, Fig. 2] — VERIFIED
| Pin | Nombre | Función |
|----|----|----|
| 1 | SDA | dato I2C (open-drain) |
| 2 | SCL | reloj I2C |
| 3 | OS  | salida overtemperature (open-drain) — dejar NC o llevar a test point |
| 4 | GND | masa |
| 5 | A2  | bit 2 de dirección |
| 6 | A1  | bit 1 de dirección |
| 7 | A0  | bit 0 de dirección |
| 8 | VCC | alimentación |

- SCL, SDA y A2..A0 **no tienen bias interno: no dejar flotantes**. [DS p.7, §7.3] — VERIFIED
- Símbolo KiCad oficial `Sensor_Temperature:LM75B` cotejado pin a pin (1=SDA … 8=+Vs);
  footprint por defecto `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` presente en librería local
  KiCad 10.0.3. — VERIFIED

## Dirección I2C
- Dirección de 7 bits = `1001 A2 A1 A0`; hasta 8 dispositivos por bus. [DS p.7, §7.3] — VERIFIED
- **Con A2=A1=A0 → GND: dirección 0x48** (1001000b). — VERIFIED (derivación directa de §7.3)

## Registro de temperatura
- Puntero de registro: 2 LSB del pointer byte; **0b00 = registro Temp**; 01 = Conf; 10 = Thyst;
  11 = Tos. [DS p.8, Table 7] — VERIFIED
- Al power-up el puntero vale 00 (Temp seleccionado); **la primera lectura es incorrecta y debe
  descartarse**. [DS p.8, §7.4.1] — VERIFIED
- Lectura Temp = **2 bytes (MSByte + LSByte)**; dato de 11 bits en complemento a dos,
  bit D10 = signo; resolución **0.125 °C/LSB**; Temp(°C) = valor_11bit × 0.125. [DS p.5 §7.1, p.9] — VERIFIED
- Conversión cada ~100 ms en modo normal (tconv ~10 ms). [DS p.5] — VERIFIED
- Bus I2C hasta 400 kHz; bus fault time-out integrado. [DS p.1, p.7] — VERIFIED
- Precisión ±2 °C (−25 a +100 °C). [DS p.1 / LCSC attrs] — VERIFIED

## Candidatos rechazados
- TMP102 (TI): solo package SOT563 1.6×1.6 mm, 68 % más pequeño que SOT-23 → soldadura manual
  difícil; spec exige soldable a mano. URL: https://www.ti.com/lit/ds/symlink/tmp102.pdf — INFERRED
  (package confirmado por página de producto TI y símbolo oficial KiCad `TMP102xxDRL`/SOT-563).
- STTS22H (ST): package UDFN-6 2×2×0.5 mm con pad expuesto (sin pines accesibles) → prohibido por
  la spec; además **sin símbolo en las librerías oficiales KiCad 10** (verificado en disco).
  URL: https://www.st.com/resource/en/datasheet/stts22h.pdf — VERIFIED (ausencia de símbolo local) /
  INFERRED (package, vía página de producto ST indexada).
