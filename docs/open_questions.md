# Preguntas abiertas — demo-vigia rev A

Preguntas que NO bloquean la generación del esquemático pero deben resolverse antes
de fabricar. Cada una tiene dueño y fase límite.

| ID | Pregunta | Dueño | Fase límite | Estado |
|---|---|---|---|---|
| Q-1 | ¿El conector SWD será header 1x5 2.54 mm (elegido) o Tag-Connect para reducir área? | usuario | antes de placement | ABIERTA — spec fija 1x5 2.54 mm por accesibilidad |
| Q-2 | ¿Se quiere serigrafía con nombre/rev/fecha y logos? | usuario | antes de Gerbers | ABIERTA — se asume sí, mínima |
| Q-3 | ¿El sensor I2C debe quedar térmicamente aislado del LDO para medir temperatura ambiente (ranuras/keep-out)? | pcb-layout-engineer | placement | ABIERTA — se documenta en pcb_constraints |
| Q-4 | ¿Ensamblado final manual o SMT service? (la spec dice `mixed`) — afecta lado de montaje único vs doble | usuario | antes de fabricar | ABIERTA — se asume montaje a una cara |
| Q-5 | ¿Se reserva GPIO/pad de expansión adicional? | usuario | antes de sellar handoff | ABIERTA — si el MCU tiene pines libres se exponen en test points |

Resolución = editar la spec si aplica (nueva revisión + ADR) o anotar decisión aquí.
