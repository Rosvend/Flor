# PQRSmart — Análisis de Modelo de Negocio
*Documento interno de estrategia — Hackathon Alcaldía de Medellín*

---

## 1. Contexto de la solución

PQRSmart es una plataforma de gestión inteligente de PQRS (Peticiones, Quejas, Reclamos y Sugerencias) diseñada para entidades públicas colombianas. Su diferenciador central es un pipeline de IA de 5 capas que procesa cada PQRS de forma automática antes de llegar al funcionario.

**Arquitectura del pipeline:**
1. Validación de entrada (¿es una PQRS real?)
2. Análisis de sentimiento — Transformer corriendo en local
3. Clasificación de secretaría — RoBERTa fine-tuned, corriendo en local
4. Deduplicación y prioridad — Embeddings con similitud coseno, corriendo en local
5. Resumen inteligente — LLM generativo vía API externa (ej. OpenAI, Anthropic, Gemini)

**Canales de entrada (multicanal):**
- Plataforma web directa
- Redes sociales (monitoreo automático de posibles PQRS)
- Llamadas telefónicas (integración con transcripción)
- Radicación física (digitalización)

**Roles de la plataforma:**
- Ciudadano: guiado por chatbot antes de radicar
- Funcionario departamental: dashboard con sus PQRS, alertas de vencimiento, resumen IA
- SuperAdmin: visión 360° de toda la entidad, estadísticas consolidadas

**Marco legal que respalda la necesidad:**
- Ley 1755 de 2015: obliga a responder en 15 días hábiles
- Ley 1581 de 2012: protección de datos personales
- Toda alcaldía en Colombia (1.102 municipios) está obligada a gestionar PQRS

---

## 2. Estructura de costos reales de la plataforma

Entender los costos propios es la base de cualquier modelo de negocio. PQRSmart tiene una estructura híbrida:

### Costos que NO escalan con el volumen (corren en local)
- Análisis de sentimiento (Transformer propio)
- Clasificación de secretaría (RoBERTa fine-tuned)
- Deduplicación y prioridad (Embeddings)
- Base de datos y almacenamiento de PQRS
- Infraestructura del servidor del municipio

Estos modelos, una vez instalados y entrenados, no generan costo por uso. El municipio los corre en su propio hardware o en un servidor dedicado. Esto es clave: **el costo no sube por más PQRS que lleguen.**

### Costos que SÍ escalan con el volumen (API externa)
- El resumen inteligente usa un LLM externo (ej. GPT-4o, Claude, Gemini)
- Este es el único componente que genera costo variable por uso
- Estimación realista: un resumen de PQRS promedio consume ~500-1000 tokens
- A precios actuales (~$0.002 USD por 1K tokens con modelos mid-tier): ~$0.001-0.002 USD por PQRS resumida
- Una alcaldía mediana procesando 10.000 PQRS/mes pagaría aprox. $10-20 USD/mes en API

**Conclusión de costos:** el costo variable de API es mínimo y perfectamente absorbible en el precio del servicio. No es un problema — es una ventaja: se puede presentar como "IA generativa incluida en el precio" sin que el margen colapse.

---

## 3. Modelo de precios: ¿Mensual o Anual?

### Argumento para precio ANUAL (recomendado para gobierno)

El gobierno colombiano no compra software como un consumidor digital. Los procesos de contratación pública en Colombia (Ley 80 de 1993, modalidades en SECOP II) trabajan con **vigencias fiscales anuales**. El presupuesto de una alcaldía se aprueba año a año. Proponer un cobro mensual genera fricciones administrativas y jurídicas innecesarias: requeriría 12 órdenes de pago, 12 justificaciones presupuestales, posibles 12 procesos de contratación menores.

Un contrato anual es más fácil de aprobar, más fácil de renovar, y genera mejor flujo de caja predecible para la startup.

**Sin embargo:** internamente, el precio anual se puede calcular como mensual × 12 con un descuento del 15-20% para hacer la propuesta atractiva vs. pagar mes a mes.

### Argumento para precio MENSUAL (solo si el cliente es privado)

Si en el futuro la plataforma se expande a organizaciones privadas (EPS, empresas de servicios públicos, grandes corporaciones con sistemas de PQRS propios), el cobro mensual es el estándar SaaS. Para ese segmento, mensual con opción de descuento anual es el modelo correcto.

### Recomendación final
- **Clientes gobierno (alcaldías, entidades públicas):** contrato anual, precio fijo
- **Clientes privados u organizaciones (fase futura):** suscripción mensual con opción anual
- En el pitch de la hackathon: hablar de "licencia anual" es la palabra que resuena con jurados que conocen el sector público

---

## 4. Estructura de precios propuesta

El precio se escala por tamaño de la entidad, no por número de usuarios ni por volumen de PQRS. Esto simplifica la negociación y evita discusiones sobre métricas de uso.

| Segmento | Referencia | PQRS estimadas/mes | Precio anual estimado (COP) |
|---|---|---|---|
| Municipio pequeño | -50.000 hab. | 200–500 | $8–15 millones |
| Municipio mediano | 50k–500k hab. | 500–5.000 | $20–50 millones |
| Ciudad grande | +500k hab. | +5.000 | $60–120 millones |
| Categoría especial | Medellín, Bogotá | +20.000 | $100–200 millones |

**Incluido en el precio:**
- Licencia de uso de la plataforma completa (3 roles)
- Pipeline de IA (análisis de sentimiento, clasificación, deduplicación, resumen)
- Integración multicanal (web, redes sociales, llamadas)
- Soporte técnico y actualizaciones
- Costo de API de resúmenes (absorbido en el precio, no se cobra aparte)
- Onboarding y capacitación inicial

**Servicios adicionales (fuera del precio base):**
- Fine-tuning del modelo RoBERTa para contexto específico del municipio: precio por proyecto
- Integraciones con sistemas legacy del municipio (ej. SAP, sistemas de archivo): precio por integración
- Reportes personalizados y analítica avanzada: módulo adicional

---

## 5. Modelo de go-to-market (cómo llegar al cliente)

### Fase 0 — Ya están aquí: la hackathon (ahora)
La hackathon ES la estrategia de entrada. Ganar valida el producto ante la propia Alcaldía de Medellín. El resultado de la hackathon se convierte en el argumento para solicitar un piloto formal.

### Fase 1 — Piloto con Medellín (0-6 meses post hackathon)
- Solicitar un piloto de 90 días con uno o dos departamentos de la Alcaldía
- Medellín tiene Ruta N y una Secretaría TIC activa — son los interlocutores correctos, no el área jurídica
- El piloto no requiere contratación formal: puede estructurarse como convenio de innovación o prueba técnica
- Objetivo del piloto: tener datos reales de reducción de tiempos y errores de enrutamiento

### Fase 2 — Primer contrato formal (6-18 meses)
- Con datos del piloto, presentar propuesta formal a través de SECOP II
- La modalidad de contratación más probable: selección abreviada de menor cuantía para contratos de software
- Medellín como primer cliente pagador y primer caso de éxito documentado

### Fase 3 — Expansión nacional (18-36 meses)
- Medellín como referencia para otras alcaldías de Antioquia y ciudades grandes
- Alianza estratégica con la Federación Colombiana de Municipios (agrupa a todos los municipios del país)
- Participación en programas como GovTechLatam del BID que conectan startups con gobiernos municipales
- Expansión a entidades que también gestionan PQRS: EPS, empresas de servicios públicos, cajas de compensación

---

## 6. Ventajas competitivas reales del modelo

**Frente a software genérico de PQRS (el competidor actual):**
- Los sistemas actuales son formularios + base de datos. No tienen IA.
- PQRSmart clasifica, prioriza y resume automáticamente: reduce el tiempo del funcionario por PQRS en un estimado del 60-70%
- El análisis de sentimiento permite detectar PQRS urgentes o de alto impacto antes de que venzan

**Frente a soluciones de IA genérica (ChatGPT, Copilot, etc.):**
- No están diseñadas para el flujo específico de PQRS colombianas
- No tienen clasificación por secretarías
- Los datos de ciudadanos no pueden salir a servidores de terceros sin consentimiento expreso — PQRSmart procesa en local

**Frente a desarrollos a medida:**
- Un desarrollo a medida para una alcaldía tarda 12-24 meses y cuesta 5-10 veces más
- PQRSmart es un producto terminado, configurable, no un desarrollo desde cero
- El costo de mantenimiento recae en PQRSmart, no en el municipio

---

## 7. Lo que se dice en el pitch (síntesis ejecutiva — 60 segundos)

El pitch sobre modelo de negocio debe cubrir exactamente esto y nada más:

1. **¿Quién paga?** La Alcaldía. El ciudadano no paga nada.
2. **¿Cómo?** Licencia anual fija. Sin costo variable por volumen de PQRS. La IA corre en local — el único costo externo son los resúmenes, que están incluidos en el precio.
3. **¿Cuánto vale el mercado?** 1.102 municipios en Colombia, todos obligados por ley a gestionar PQRS. Medellín es el piloto. El resto es el mercado.
4. **¿Cuál es el siguiente paso?** Piloto de 90 días con la Alcaldía para demostrar reducción real de tiempos.

**Guión textual:**
*"El modelo es simple. La Alcaldía paga una licencia anual — como cualquier software empresarial. El ciudadano recibe el servicio gratis. El precio es fijo sin importar cuántas PQRS lleguen, porque casi todo corre en local. El único costo variable son los resúmenes de IA, y es marginal — está incluido en el precio. Medellín es nuestro caso de éxito inicial. Y cuando lo tengamos, cada una de las 1.102 alcaldías de Colombia — todas obligadas por ley a gestionar PQRS — es un cliente potencial."*

---

*PQRSmart — Documento de uso interno del equipo*
