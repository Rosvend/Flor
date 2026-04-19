# PQRSmart — Script Completo del Pitch
*Duración: 8-10 minutos | Hackathon Alcaldía de Medellín*

---

## SLIDE 1 — PORTADA
**[Abrir con pausa. Dejar que lean el nombre. Hablar despacio.:]**

"Medellín se llama a sí misma el Distrito de Innovación y Tecnología.

Pero un ciudadano que espera 45 días para recibir una respuesta genérica
a una queja que mandó tres veces al departamento equivocado...
no siente eso.

Nosotros venimos a cerrar esa brecha.
Somos **PQRSmart**."

---

## SLIDE 2 — EL PROBLEMA
**[Hablar como si estuvieras contando algo que le pasó a alguien real:]**

"Imagínense esto. Una persona manda una PQRS sobre una obra que lleva meses
bloqueando su negocio. La radica por la plataforma web. Llega al departamento equivocado.
La redirigen. Pasan 15 días. Vence el plazo legal. El ciudadano no sabe nada.
Llama. Le dicen que está 'en proceso'.

Eso no es falla de los funcionarios.
Es falla del sistema.

Y la ley es clara: la Ley 1755 de 2015 obliga a responder en 15 días hábiles.
El incumplimiento acarrea sanción disciplinaria.

Hoy, en solo el departamento de espacio público,
Medellín gestionó más de 2.236 PQRS en 2025.
Eso es solo un departamento.
Imaginen el volumen real de toda la alcaldía.

El problema no es falta de voluntad.
Es falta de inteligencia en el proceso."

---

## SLIDE 3 — EL EMBUDO MULTICANAL
**[Aquí el tono cambia — empieza la solución. Más seguro, más rápido:]**

"El primer problema que resolvemos es la fragmentación.

Hoy un ciudadano puede radicar una PQRS de cinco formas distintas:
en persona, llamando, por la plataforma web,
o simplemente dejando un comentario en redes sociales.

Cada canal va por su lado. No hay un cerebro central.

PQRSmart crea un embudo.
Todos los canales desembocan en un único sistema inteligente.

Y si alguien escribe una queja en Twitter o en Instagram,
nuestro sistema la detecta automáticamente,
valida si es una PQRS real, y la ingresa al flujo.

El ciudadano no necesita saber cómo funciona por dentro.
Solo necesita sentir que alguien lo está escuchando."

---

## SLIDE 4 — EL PIPELINE DE IA
**[Este es el slide más importante. Hablar con orgullo técnico pero sin perder al jurado:]**

"Ahora, lo que hace diferente a PQRSmart de cualquier otro software de gestión de PQRS:
tenemos un pipeline de inteligencia artificial de cinco capas.
Y esto es importante: **todo corre en local.**

Sin dependencia de APIs externas. Sin datos ciudadanos saliendo del servidor.
Sin costos que escalen con el volumen. Una vez instalado — funciona.

Veamos qué hace cada capa:

**Capa 1 — Validación.**
Antes de entrar al sistema, se verifica que lo que llegó realmente sea una PQRS.
Filtramos spam, mensajes irrelevantes, duplicados por canal.

**Capa 2 — Análisis de sentimiento.**
Un modelo Transformer entrenado analiza el tono de la petición.
¿Está la persona angustiada? ¿Usa lenguaje ofensivo?
Esto permite priorizar los casos más urgentes y manejar adecuadamente los más sensibles.
Este modelo corre completamente en local.

**Capa 3 — Clasificación automática.**
Aquí entra RoBERTa — un modelo de lenguaje fine-tuneado específicamente
para entender a qué secretaría pertenece cada PQRS.
¿Es movilidad? ¿Espacio público? ¿Medio ambiente?
El sistema lo determina solo, sin intervención humana.
Corre en local.

**Capa 4 — Deduplicación y prioridad.**
Con embeddings vectoriales, el sistema identifica si ya existe una PQRS similar.
Si cincuenta personas se quejaron del mismo hueco en la misma calle,
eso no se procesa cincuenta veces — se agrupa, se prioriza, se resuelve una vez.
Corre en local.

**Capa 5 — Resumen inteligente.**
Un modelo de lenguaje generativo — corriendo también en local,
usando la misma infraestructura de la alcaldía —
produce un resumen ejecutivo de la PQRS para el funcionario.

El funcionario no lee una queja de ochocientas palabras.
Lee tres líneas. Entiende el caso. Toma acción.

Cinco modelos. Cero dependencias externas.
Cero pago por token. Cero riesgo de privacidad.
La alcaldía literalmente compra el sistema y lo tiene para siempre."

---

## SLIDE 5 — LA PLATAFORMA (3 roles)
**[Rápido y visual. Uno, dos, tres:]**

"Esto se traduce en tres experiencias:

**El ciudadano** entra a la plataforma y encuentra un chatbot que lo guía.
Antes de radicar, el sistema ya sabe a dónde va esa PQRS.
No hay margen para el error de enrutamiento.

**El funcionario de cada departamento** abre su dashboard
y ve solo las PQRS que le corresponden.
Tiene el resumen de IA, la categoría, el nivel de urgencia,
y el plazo legal contando regresivamente.
No hay excusa para no responder a tiempo.

**El SuperAdmin** tiene visión total.
Estadísticas por departamento, tiempos promedio de respuesta,
PQRS próximas a vencer, tendencias por tipo de solicitud.
La alcaldía deja de operar a ciegas."

---

## SLIDE 6 — IMPACTO
**[Volver a lo humano. El número más importante no es técnico:]**

"Pero ¿saben cuál es el verdadero impacto de todo esto?

No es el porcentaje de reducción de PQRS mal dirigidas.
No es el ahorro en tiempo de funcionarios.

Es esto:

Un ciudadano manda una PQRS un lunes.
El jueves recibe una respuesta real, clara, del departamento correcto.

Ese ciudadano no lo va a olvidar.

Va a pensar: 'aquí sí funciona algo'.
Va a sentir, por primera vez, que vive en un distrito de innovación y tecnología
que no es solo un eslogan en una valla.

Eso es confianza institucional.
Y la confianza institucional no se mide en eficiencia operativa —
se mide en ciudadanos que creen en su gobierno.

En números: estimamos una reducción del 70% en PQRS mal dirigidas
y cumplimiento consistente del plazo legal de 15 días.
Pero la métrica que más nos importa es esa —
el ciudadano que siente que lo escucharon."

---

## SLIDE 7 — MODELO DE NEGOCIO
**[Directo. Sin rodeos. Una, dos, tres frases y listo:]**

"El modelo es simple.

La Alcaldía adquiere una licencia anual — como cualquier software institucional.
El ciudadano no paga nada.

Y como todo corre en local —
los modelos de IA, los embeddings, los resúmenes, todo —
el precio es fijo sin importar si llegan mil PQRS al mes o diez mil.
No hay costo que escale. No hay sorpresas.

Medellín es el primer cliente y el caso de éxito que abre el mercado.
Porque Colombia tiene 1.102 municipios.
Todos están obligados por ley a gestionar PQRS.
Todos son clientes potenciales.

El camino es claro: piloto aquí, expansión nacional después."

---

## SLIDE 8 — CIERRE
**[Pausa larga antes de empezar este slide. Mirar al jurado. Hablar despacio:]**

"Medellín compite con las mejores ciudades del mundo
en innovación, en tecnología, en transformación urbana.

Pero la innovación que más importa no es la que se ve en un edificio nuevo.
Es la que siente el ciudadano cuando el gobierno responde.
Cuando la queja que mandó el lunes tiene respuesta el jueves.
Cuando no tiene que llamar tres veces para saber en qué va su caso.

PQRSmart no es solo una plataforma.
Es la infraestructura que convierte la promesa de Medellín Innova
en algo que la gente puede tocar, sentir y confiar.

Porque cada PQRS es una persona.
Y cada persona merece una respuesta.

Somos PQRSmart. Gracias."

---

## NOTAS PARA EL EXPOSITOR

**Sobre el ritmo:**
- Slides 1-2: lento, emocional. Que cale el problema.
- Slides 3-4: más rápido, técnico pero claro. Aquí demuestran que saben lo que hacen.
- Slides 5-6: equilibrado. Concreto y humano al mismo tiempo.
- Slides 7-8: slide 7 rapidísimo, slide 8 muy lento. El cierre se saborea.

**Frases para tener listas en Q&A:**

Si preguntan por privacidad de datos:
→ "Todo corre en local. Ningún dato ciudadano sale del servidor de la alcaldía. Cumplimos la Ley 1581 sin necesidad de contratos con terceros."

Si preguntan por precisión de la clasificación:
→ "En nuestras pruebas el modelo clasifica con más del 85% de precisión. Y cuando no está seguro, el sistema lo señala para revisión humana. No reemplaza al funcionario — lo hace más eficiente."

Si preguntan por costo de implementación:
→ "Licencia anual fija. Sin costo por volumen, sin costo de API, sin sorpresas. La alcaldía sabe exactamente cuánto paga desde el primer día."

Si preguntan por la competencia:
→ "Los sistemas actuales son formularios conectados a una base de datos. No tienen IA. No clasifican. No priorizan. No resumen. Son el problema disfrazado de solución."

Si preguntan si esto ya existe:
→ "Tenemos MVP funcional. No estamos vendiendo una idea — estamos pidiendo que lo vean funcionar."

**Lo que NUNCA se dice en el pitch:**
- No mencionar SECOP II ni licitaciones públicas.
- No dar cifras exactas de precio.
- No hablar de expansión internacional.
- No disculparse por nada.

---

*PQRSmart — Script interno del equipo de presentación*
