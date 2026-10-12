# Herramientas comerciales/AI de EDA — Evaluación objetiva (julio 2026)

**Contexto:** estudio comparativo para un pipeline agéntico local (KiCad + MCP + Python, Windows 11) que va de requisitos en lenguaje natural → esquemático → PCB → fabricación.
**Restricciones:** sin subir IP a cloud, sin crear cuentas, sin comprar. Solo investigación pública.
**Etiquetas:** `VERIFIED` = confirmado en documentación oficial, foros o prensa técnica independiente. `INFERRED` = deducción razonable de evidencia parcial. `UNVERIFIED` = afirmación de marketing o dato no confirmable sin cuenta.

---

## 1. Flux.ai

### Qué hace (verificado vs prometido)
- `VERIFIED` Producto activo en 2026. EDA cloud-nativo (navegador) con agente de IA ("Copilot", ahora agente con "ACUs") que genera esquemáticos desde lenguaje natural, hace BOM, footprints desde datasheets PDF, y auto-layout con IA. Actualización "Spring 2026": agente autocorregible, sourcing con precios en tiempo real.
- `VERIFIED` (evidencia independiente, HN jun-2026): usuarios reportan resultados muy pobres — uno gastó $50–100 en tokens y "no consiguió más que un par de componentes simples en el esquemático en posiciones sensatas"; otro perdió $60 y el soporte no respondió. Consenso del hilo: los usuarios obtienen mejores resultados con **KiCad + MCP + SKIDL** que con Flux. Fuente: hilo HN item 48368721.
- `UNVERIFIED` Las afirmaciones de "10x más rápido" y "layouts que necesitan menos limpieza" provienen solo del blog de Flux.

### Interoperabilidad con KiCad
- `VERIFIED` **Importa** librerías de partes KiCad y esquemáticos Altium (ASCII)/Cadence (EDIF). **No importa layouts.**
- `VERIFIED` **Exporta** solo Gerbers RS-274X, drill, BOM, pick-and-place y netlists. **No exporta a formato KiCad ni Altium** (Enterprise menciona JEP30). Hilo del foro KiCad "Converting Flux.ai projects to KiCAD" confirma que no hay ruta directa proyecto→KiCad.
- `INFERRED` Interoperabilidad real con KiCad: **unidireccional y con pérdida**. Una vez diseñas en Flux, el diseño editable vive en Flux (lock-in fuerte).

### API / automatización externa
- `UNVERIFIED` docs.flux.ai lista una sección "API", pero el contenido no es accesible públicamente y ninguna fuente independiente documenta una API REST para dirigir el agente o exportar diseños programáticamente. Su Privacy Statement menciona "pulling data via our API" solo para contenido público.
- `INFERRED` No existe automatización externa viable para un pipeline headless local.

### Coste y privacidad
- `VERIFIED` Planes de pago desde ~$15/mes; Pro ~$158/mes/editor; Teams ~$120/mes/editor anual. IA medida en ACUs (100/mes incluidos, $2 por ACU extra).
- `VERIFIED` **Los proyectos gratuitos son públicos** (indexables por buscadores); proyectos privados, exportación y uso de IA requieren plan de pago. Incompatible con la restricción de no subir IP.
- `VERIFIED` Riesgo reputacional/confianza: en mayo-junio 2026 Flux envió una carta de demanda (vía Fenwick, con reclamaciones CFAA) a **Adafruit** para impedir la publicación de una divulgación responsable de una **misconfiguración de servidor que exponía datos de usuarios**. Adafruit contrademandó. Cobertura en Slashdot/HN. Esto afecta directamente a la evaluación de privacidad de un proveedor cloud.

### Veredicto: **DESCARTAR**
Cloud-only con proyectos públicos en tier gratuito (viola la restricción de IP), sin exportación editable a KiCad, sin API pública documentada, calidad de generación IA cuestionada por usuarios independientes, e historial reciente de seguridad y de respuesta legal agresiva a la divulgación responsable.

---

## 2. Quilter (quilter.ai)

### Qué hace (verificado vs prometido)
- `VERIFIED` Producto activo. **No genera esquemáticos**: automatiza **placement + routing** de PCBs a partir de un diseño existente, usando reinforcement learning "guiado por física" (simula DRC/SI). Genera múltiples candidatos de layout en paralelo.
- `VERIFIED` (independiente): caso HN dic-2025 "Linux computer designed with AI boots on first attempt" — Quilter rutó una placa de 843 componentes en ~27 h de cómputo con limpieza mínima; comentaristas puntualizan que Quilter **rutó**, no "diseñó", el computador. Un usuario (krasin, HN) confirma placa fabricada con éxito desde el trial.
- `VERIFIED` (docs/blog propios) Limitaciones: óptimo en 100–1.000 componentes y 2.000–5.000 pines, densidad de pines <20%; **solo vías pasantes** (blind/buried en desarrollo); fan-out BGA en beta; **las redes RF deben pre-rutarse a mano** antes de enviar.
- `UNVERIFIED` Los benchmarks "placement en 45 min vs 4 h" provienen del blog de Quilter (marketing).

### Interoperabilidad con KiCad
- `VERIFIED` Lee y escribe **archivos nativos de KiCad, Altium, Allegro/OrCAD y Xpedition**: subes el proyecto, revisas cómo interpreta constraints, y recibes de vuelta el archivo nativo editable en tu CAD. Versiones exactas de KiCad soportadas: no publicadas (`UNVERIFIED`).
- `VERIFIED` Workflow híbrido soportado: tú pre-colocas/pre-rutas el 20% crítico y Quilter hace el resto.

### API / coste / privacidad
- `UNVERIFIED` No hay API pública documentada; el flujo es upload por web (requiere cuenta).
- `VERIFIED` Precio: exploración/iteración gratuita, **pagas solo por diseños aprobados**, precio escala por nº de pines a rutar (pines pre-rutados no cuentan). Cifras concretas no públicas.
- `VERIFIED` Cloud SOC 2 Type 2 en AWS; existe opción **self-hosted** (Kubernetes + GPU NVIDIA, decenas de GB de RAM) — orientada a enterprise, resolvería la restricción de IP pero presumiblemente con coste enterprise (`INFERRED`).

### Veredicto: **EVALUAR EN FASE FUTURA**
Es la herramienta comercial más compatible con un pipeline KiCad (entrada/salida nativa KiCad editable) y la única con evidencia independiente de resultados fabricables. Pero exige cuenta y subir el diseño al cloud (viola restricciones actuales), no tiene API pública, y no cubre esquemáticos. Si en el futuro se relaja la restricción de IP (o se negocia self-hosted), es el candidato natural para el eslabón placement/routing.

---

## 3. JITX

### Qué hace (verificado vs prometido)
- `VERIFIED` Activo. Plataforma de "software-defined electronics": defines el circuito en código y sus solvers automatizan selección de componentes, pin assignment, drafting de esquemático y checks. Fundada 2017 (YC S18), Series A de Sequoia.
- `VERIFIED` **Pivote de lenguaje**: abandonó su DSL sobre Stanza y se reconstruyó en **Python nativo**, lanzado en Q4 2025 con early access — motivado explícitamente por que "la IA escriba todo el código" (los LLMs manejan Python mucho mejor que un DSL propio). Corre como extensión de VSCode.
- `VERIFIED` Publica repos abiertos: `open-components-database` y `jitx-skills` (skills para agentes de código) en GitHub.
- `UNVERIFIED` Calidad real del flujo Python + routing en 2026: la única review independiente (eddiesamuels.com, jun-2026) dice que "sus nuevas herramientas de routing parecen muy usables" pero no las retestó.

### Interoperabilidad con KiCad
- `VERIFIED` Exporta a **KiCad y Altium** (docs oficiales: docs.jitx.com/cad-integration/exporting, con página de erratas específica de KiCad). El flujo previsto: generar en JITX, finalizar placement/routing y fabricación en tu CAD.

### Acceso / coste / curva
- `VERIFIED` Plan gratuito para proyectos open source; precio "contact us" para empresas. El acceso general al producto Python era early-access con registro a finales de 2025 (`VERIFIED` entonces; estado exacto en jul-2026 `UNVERIFIED`).
- `INFERRED` Curva de aprendizaje: alta históricamente (DSL propio); el paso a Python + skills para agentes la reduce, pero sigue siendo "programar hardware", no dibujar.

### Veredicto: **EVALUAR EN FASE FUTURA** (vigilar de cerca)
Filosóficamente es lo más cercano al pipeline del usuario (código → esquemático+layout → export a KiCad, pensado para que lo escriba un LLM). Pero requiere cuenta/early-access, el runtime no es open source, y no hay evidencia independiente de madurez del flujo Python. Mientras tanto, el mismo patrón se cubre localmente con SKIDL/atopile/tscircuit + KiCad. Reevaluar cuando el acceso Python sea general y haya reviews.

---

## 4. Otras herramientas AI-EDA (fichas breves)

### DeepPCB (InstaDeep/BioNTech)
- `VERIFIED` Autorouter cloud (placement + routing) por RL. Soporte nativo Zuken y **KiCad**; importa Altium/EasyEDA/Eagle/Proteus. Tier público: hasta 1.000 componentes, 2.200 pines, 8 capas; free tier + pay-as-you-go con sistema de créditos que la review independiente (eddiesamuels) califica de confuso.
- `INFERRED` Solapa con Quilter pero con menos tracción visible y dueño (farmacéutica BioNTech) cuyo foco no es EDA. Veredicto: **descartar** (mismo bloqueo cloud/cuenta que Quilter, con menos evidencia de calidad).

### Celus
- `VERIFIED` Plataforma AI para fase temprana: de diagrama de bloques/requisitos propone circuitos, genera esquemático, BOM y floorplan, con salida a formatos EDA nativos. Orientada a cuenta cloud y catálogo propio.
- Veredicto: **descartar** (cloud, cuenta, y automatiza justo la parte que el pipeline del usuario ya hace con LLM local).

### CircuitMind
- `VERIFIED` Enterprise, acceso solo con demo comercial; genera opciones de diseño optimizando componentes por coste/tamaño/consumo. Sin acceso público. Veredicto: **descartar**.

### Diode Computers (YC)
- `VERIFIED` (review eddiesamuels) Diseño por código con DSL propio ("Zener"), exporta a KiCad; buen tooling de visualización y pedido; integración con servicios de IA. Aún inmaduro. Veredicto: **vigilar**, no integrar.

### tscircuit — open source, relevante
- `VERIFIED` Circuitos como componentes React/TypeScript; MIT/open source; registry de paquetes npm; **importa/exporta KiCad** (incl. librerías vía KiCad PCM); documentación oficial de "circuit generation with AI" y un **MCP server del registry** — es decir, integración directa con agentes tipo Claude Code/Codex (demo pública de Adafruit, mayo-2026).
- `INFERRED` Autorouting propio aún cuestionado (review independiente). Veredicto: **integrar ahora** como pieza open source complementaria (no comercial).

### atopile — open source, relevante
- `VERIFIED` Lenguaje declarativo `.ato` + compilador; trabaja nativamente con KiCad; desarrollo activo (v0.15.7, abril 2026); sistema público de paquetes con bloques pre-rutados. Componente cloud/AI: mínimo/opcional.
- Veredicto: **integrar ahora** (open source, local, complementa el pipeline).

### Altium (365 Copilot) y Cadence (Allegro X AI)
- `VERIFIED` Ambos incumbentes integran IA: Altium 365 con sugerencias de componentes/asistentes cloud; Cadence Allegro X AI con placement generativo, routing ML y DFM automático (cloud, enterprise).
- Veredicto: **descartar** para este proyecto (licencias comerciales caras, ecosistemas cerrados, cloud; irrelevantes para un pipeline KiCad local).

---

## 5. APIs de datos de componentes para BOM/sourcing

| API | Tier gratuito | Aprobación | Datos | Notas |
|---|---|---|---|---|
| **Nexar (Octopart)** | `VERIFIED` Plan Evaluation gratuito (~100 partes emparejadas; referencias también a "Welcome 1K" = 1.000 llamadas/mes) | Registro en portal Nexar | Precios multi-distribuidor, stock, lead time, **lifecycle**, datasheets, specs, modelos ECAD (en tier de evaluación) | GraphQL. El free tier es de evaluación, muy limitado para producción (`VERIFIED`); fuentes de foro indican que el acceso gratuito amplio ya no existe salvo estudiantes (`UNVERIFIED`) |
| **Mouser** | `VERIFIED` Gratuita con cuenta My Mouser; clave API (UUID, sin OAuth) | Alta simple, 1–2 días laborables | Búsqueda por palabra clave/paramétrica, precio, stock | Límite ~30 req/min (`VERIFIED` por usuarios); límite diario no publicado oficialmente (`UNVERIFIED`, se cita ~1.000/día) |
| **Digi-Key** | `VERIFIED` Gratuita: sandbox inmediato; producción requiere crear/pertenecer a una organización | Registro developer.digikey.com; OAuth2 (2-legged para búsqueda) | ProductSearch v4: precio, stock, parámetros, datasheets, sustitutos | La más rica de los distribuidores; OAuth añade fricción a scripts |
| **JLCPCB** | `VERIFIED` API oficial (api.jlcpcb.com): Parts API (stock/precio/specs de su librería), pedidos PCB/SMT | `VERIFIED` **Aprobación selectiva**: revisan historial de pedidos y perfil de empresa; no todos los solicitantes son aprobados | Partes de la librería JLCPCB (crítico para ensamblaje JLC), pedidos automatizados | Alternativa sin API: plugin open source `kicad-jlcpcb-tools` usa la base de partes desde KiCad sin cuenta API |
| **LCSC** | `VERIFIED` Existe API con FAQ pública (límites de frecuencia, precios con descuento, tiempo real) | Solicitud a LCSC; detalles de elegibilidad no públicos (`UNVERIFIED`) | Stock, precio, detalles de artículo | Datos solapan con JLCPCB Parts |

**Implicación para el pipeline** (`INFERRED`): todas requieren crear cuenta (contra la restricción actual). Cuando se relaje: Mouser (fricción mínima) + Digi-Key (datos más ricos) como par principal; Nexar solo si se necesita lifecycle/multi-distribuidor y se acepta el límite del tier de evaluación; JLCPCB Parts vía plugin KiCad open source **ya es usable hoy sin API**.

---

## 6. Tabla resumen de veredictos

| Herramienta | Aporta | Bloqueos vs restricciones | Veredicto |
|---|---|---|---|
| Flux.ai | Esquemático IA cloud (calidad cuestionada) | Cloud-only, proyectos gratuitos públicos, sin export KiCad, sin API, incidente seguridad/legal 2026 | **Descartar** |
| Quilter | Placement+routing autónomo, I/O KiCad nativo, evidencia independiente | Cuenta + upload cloud, sin API pública, sin esquemático, límites (vías pasantes, RF manual) | **Evaluar en fase futura** |
| JITX | Código Python → esquemático+layout → export KiCad, pensado para LLMs | Early access, runtime cerrado, madurez sin verificar | **Evaluar en fase futura** |
| DeepPCB | Autorouter cloud con soporte KiCad | Cloud/cuenta, créditos confusos, menos tracción | Descartar |
| Celus / CircuitMind | Esquemático/BOM generativo enterprise | Cloud, demo-gated, duplica el rol del LLM local | Descartar |
| tscircuit | Circuitos-como-código TS, MCP server, I/O KiCad, open source | Routing propio inmaduro | **Integrar ahora** |
| atopile | Lenguaje `.ato` + KiCad nativo, local, open source | Ecosistema joven | **Integrar ahora** |
| Altium/Cadence AI | IA en incumbentes enterprise | Coste, lock-in, cloud | Descartar |
| APIs componentes | Datos BOM/sourcing programáticos | Todas requieren cuenta; JLCPCB aprueba selectivamente | Mouser/Digi-Key cuando se permita cuenta; plugin JLCPCB ya |

---

## Fuentes principales
- Flux: flux.ai/p/pricing · docs.flux.ai (export, private-and-public-projects, kicad-to-flux) · HN 48368721 y 48368121 (Adafruit) · Slashdot 2026-06-02 · forum.kicad.info hilos 40449 y 59947
- Quilter: quilter.ai/pricing · HN 46294254 (dic-2025, placa Linux 843 componentes) · blog quilter.ai (marketing, usado solo como autodescripción)
- JITX: jitx.com · blog.jitx.com "What's new in JITX 2025" y FAQ · docs.jitx.com/cad-integration · github.com/JITx-Inc
- Review independiente multiherramienta: eddiesamuels.com/blog/ai-pcbs (jun-2026)
- Otros: deeppcb.ai · instadeep.com · protoflow.ai/compare · docs.tscircuit.com · pypi.org/project/atopile · blog.adafruit.com (tscircuit, mayo-2026)
- APIs: nexar.com/api y compare-plans · mouser.com/api-hub · developer.digikey.com · api.jlcpcb.com · lcsc.com/faqs/api
