# OMEGAHACK 2026 Documento Oficial del Reto

_Este documento es confidencial. Solo puede circular entre participantes activos del evento._
Empresa aliada
**Alcaldía de Medellín**
Secretaría
**Secretaría de Desarrollo Económico**
Tiempo de desarrollo
**20 horas efectivas**


## 1. CONTEXTO DEL RETO

OmegaHack 2026 es una competencia multidisciplinaria organizada por el Grupo Estudiantil
NOVA de la Universidad EAFIT. El reto de esta edición es planteado por la Secretaría de
Desarrollo Económico de la Alcaldía de Medellín y se enmarca en tecnología aplicada a la
sostenibilidad organizacional del sector público.
La Secretaría de Desarrollo Económico gestiona un volumen significativo de PQRSDs
(Peticiones, Quejas, Reclamos, Sugerencias y Denuncias) provenientes de la ciudadanía. Estas
solicitudes constituyen un derecho fundamental consagrado en la Constitución Política
colombiana, y la entidad tiene la obligación legal de darles respuesta dentro de un plazo máximo
de 15 días hábiles.
El proceso actual presenta fricciones que dificultan el cumplimiento oportuno de este deber. La
herramienta que diseñen los equipos deberá atacar esas fricciones sin reemplazar el criterio
humano en la validación y respuesta final: la meta es optimizar y automatizar las partes del
proceso que no requieren juicio profesional, para que los funcionarios puedan concentrarse en la
revisión y el aval de las respuestas.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 2. CANALES DE RECEPCIÓN Y ALCANCE DEL RETO

El reto abarca todos los canales por los que la Secretaría recibe PQRSDs, no solo el sistema
oficial:
**Canales oficiales**
Son los canales institucionales que permiten radicación formal, trazabilidad y seguimiento en el
sistema de gestión (Mercurio):

- Portal web de la Alcaldía de Medellín.
- Atención presencial en las sedes de Servicio a la Ciudadanía (21 sedes en total).
- Canal virtual o telefónico gestionado por la Subsecretaría de Servicio a la Ciudadanía.
**Canales no oficiales**
Son medios que no siguen protocolos institucionales de radicación formal, no son medibles ni
trazables en el sistema, pero igualmente generan obligación de respuesta. Representan una
parte del volumen real de solicitudes:
- Correo electrónico personal o institucional de funcionarios y directivos.
- Redes sociales de la Alcaldía o de sus dependencias.
- WhatsApp u otras plataformas de mensajería a directivos.
_El reto NO se limita a las PQRSDs que ingresan por Mercurio. La solución debe contemplar
también las solicitudes que llegan por canales no oficiales, que igualmente requieren respuesta
oportuna y cuya ausencia de trazabilidad es en sí misma parte del problema.
Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 3. PROCESO ACTUAL DE GESTIÓN

El flujo actual de una PQRSD tiene dos etapas de clasificación antes de llegar a quien debe
responderla:
**Etapa 1 — Clasificación por Servicio a la Ciudadanía (BackOffice)**
Una vez el ciudadano radica la PQRSD por cualquier canal oficial, la Subsecretaría de Servicio a
la Ciudadanía realiza la primera clasificación: determina cuál de las 26 dependencias de la
Alcaldía es competente para dar respuesta. Esta clasificación se apoya en una Matriz Temática
gestionada por la misma subsecretaría. El resultado es el enrutamiento de la solicitud a la
dependencia correspondiente a través del sistema Mercurio.
**Etapa 2 — Clasificación interna en la Secretaría de Desarrollo Económico**
Al recibir la PQRSD, el enlace de la Secretaría realiza una revisión interna para determinar qué
subsecretaría o dependencia dentro de la Secretaría de Desarrollo Económico debe atenderla,
según el tema y la solicitud específica del ciudadano. Ejemplo: si es una solicitud de empleo, se
remite a la Subsecretaría de Creación y Fortalecimiento Empresarial; si es una solicitud de
crédito, se direcciona al Banco Distrital.
**Seguimiento y cierre**
El enlace hace seguimiento al vencimiento de los términos. Cuando faltan 3 días hábiles para el
vencimiento de la PQRSD, verifica si ya cuenta con respuesta y, en caso contrario, envía un
recordatorio al responsable indicando la proximidad del vencimiento. Una vez se cuenta con la
respuesta y se notifica al ciudadano, la solicitud es evacuada del sistema Mercurio y archivada
digitalmente.
**Tipos de PQRSDs por número de dependencias involucradas**

- Unidependencia: la solicitud es competencia de una sola dependencia de la Alcaldía. Es
    el caso más común.
- Multidependencia: la solicitud involucra varias dependencias con competencias distintas
    sobre partes diferentes de la misma petición. En estos casos, Servicio a la Ciudadanía
    genera radicados individuales por cada dependencia involucrada.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 4. CAUSAS RAÍZ DEL PROBLEMA

La Secretaría identificó tres causas raíz que dificultan la gestión oportuna de PQRSDs:
**Causa 1 — Clasificación errónea por desconocimiento de competencias**
Los ciudadanos frecuentemente no conocen las funciones específicas de las 26 dependencias
de la Alcaldía y dirigen sus PQRSDs guiándose por asociación de palabras, no por competencia
real. Esto genera un flujo constante de solicitudes mal enrutadas que deben ser redirigidas
internamente, consumiendo tiempo del proceso y erosionando el plazo de 15 días.
Ejemplo documentado: una solicitud sobre el estado de rampas para personas con discapacidad
llega a la Secretaría de Movilidad (por asociación con accesibilidad urbana), cuando la
competencia le corresponde a la Secretaría de Infraestructura.
**Causa 2 — Información clave enterrada en textos de alta densidad**
Las PQRSDs se redactan en lenguaje natural —lo cual es un derecho del ciudadano protegido
por la ley, no el problema en sí—. Con frecuencia, la solicitud concreta aparece al final de textos
muy extensos; se han documentado casos de hasta siete páginas. Esto obliga a los funcionarios
revisores a leer el documento completo antes de identificar qué se está pidiendo, ralentizando
cada instancia del proceso.
**Causa 3 — Ausencia de registro estructurado de precedentes**
No existe un historial organizado y consultable de PQRSDs resueltas anteriormente. Ante casos
similares o idénticos a otros ya respondidos, los funcionarios deben repetir todo el proceso de
verificación desde cero, sin poder apoyarse en resoluciones previas. El trabajo ya fue realizado,
pero no hay manera de recuperarlo eficientemente.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 5. OBJETIVO DEL RETO

**Diseñar y desarrollar un MVP (Minimum Viable Product) que optimice el proceso
de gestión de PQRSDs de la Secretaría de Desarrollo Económico, atacando al
menos las tres causas raíz identificadas, sin reemplazar el criterio humano en la
validación y respuesta final.**
La herramienta no tiene como objetivo reemplazar a los funcionarios. Su propósito es reducir la
carga de las tareas que no requieren criterio profesional —clasificación inicial, enrutamiento,
síntesis del contenido— para que las personas puedan concentrarse en la revisión técnica o
jurídica y en el aval final de las respuestas. El Asesor Jurídico de la Secretaría debe aprobar
cada respuesta antes de ser enviada; cualquier solución debe contemplar ese paso humano
como inamovible.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 6. COMPONENTES FUNCIONALES ESPERADOS

La entidad aliada identificó tres funcionalidades que debería ofrecer la herramienta. Los equipos
tienen libertad para proponer la arquitectura técnica y el alcance de cada componente, siempre
que respondan a las causas raíz:
**Componente A — Parametrización de competencias (base de conocimiento)**
Construcción de una base de conocimiento estructurada con las funciones, alcances y
competencias legales de cada una de las 26 dependencias de la Alcaldía de Medellín. Esta
información es de carácter público y está disponible en los portales web institucionales. Es el
insumo base que habilita la pre-clasificación automática. Sin esta parametrización, los demás
componentes no tienen criterio sobre el cual operar.
**Componente B — Pre-clasificación automática de PQRSDs**
A partir de la base de competencias, la herramienta debe ser capaz de leer el contenido de una
PQRSD entrante y determinar a cuál dependencia de la Alcaldía corresponde, y —en el caso de
PQRSDs dirigidas a la Secretaría de Desarrollo Económico— a cuál subsecretaría interna debe
ser remitida. El término correcto es pre-clasificación: la herramienta propone, el funcionario
valida. Esto ataca directamente la Causa 1.
**Componente C — Síntesis y resumen estructurado**
La herramienta debe generar un resumen ejecutivo de cada PQRSD que facilite la revisión por
parte del enlace y del Asesor Jurídico. La entidad planteó una estructura de al menos tres
capas: (1) un lead o encabezado con la solicitud concreta identificada, (2) una discriminación
temática del contenido, y (3) la PQRSD completa como respaldo. El formato exacto de entrega
—correo estructurado, panel de gestión u otro— es libre para los equipos. Este componente
ataca la Causa 2 y parcialmente la Causa 3.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 7. ACTORES DEL PROCESO

**Actor Rol en el proceso
Ciudadanía** Genera y envía las PQRSDs por cualquier canal, en lenguaje
natural y sin estructura formal. Es un derecho fundamental; no
puede exigírsele formato específico.
**BackOffice / Servicio a la
Ciudadanía**
Realiza la primera clasificación: determina cuál de las 26
dependencias es competente y enruta la PQRSD a través de
Mercurio.
**Enlace de la Secretaría
de Desarrollo Económico**
Recibe la PQRSD ya enrutada y determina qué subsecretaría o área
interna debe atenderla. Hace seguimiento al vencimiento de
términos y envía alertas a 3 días del límite.
**Asesor Jurídico** Da el aval legal antes de que cualquier respuesta sea enviada al
ciudadano. Por su despacho debe pasar cada respuesta. Requiere
síntesis claras para agilizar este paso.
**Secretaría de Desarrollo
Económico**
Entidad aliada del reto. Opera junto a otras 25 dependencias de la
Alcaldía. Cada dependencia tiene competencias legales
estrictamente delimitadas.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 8. MARCO LEGAL RELEVANTE

El reto se desarrolla dentro de un contexto legal específico que los equipos deben conocer para
garantizar que sus propuestas sean viables en la práctica:

- Ley 1755 de 2015: Regula el Derecho Fundamental de Petición. Establece plazos,
    modalidades y obligaciones de respuesta.
- Ley 1437 de 2011: Código de Procedimiento Administrativo y de lo Contencioso
    Administrativo.
- Ley 1474 de 2011: Establece la obligación de tener una dependencia encargada de
    recibir, tramitar y resolver las PQRSDs.
- Ley 1581 de 2012: Protección de datos personales. Cualquier herramienta que procese
    PQRSDs maneja datos sensibles de los ciudadanos y debe cumplir esta ley.
- Decreto Municipal 883 de 2015: Define las funciones de la Secretaría de Gestión
    Humana y Servicio a la Ciudadanía de Medellín.
_Implicación práctica para los equipos: la herramienta NO puede generar respuestas automáticas
al ciudadano sin aval humano. Tampoco puede rechazar o archivar solicitudes de forma
autónoma. Cualquier acción que genere un efecto legal hacia el ciudadano requiere validación
por parte de un funcionario autorizado.
Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 9. ENTREGABLE ESPERADO

Al finalizar las 20 horas de desarrollo efectivo, cada equipo deberá presentar:

- Un MVP navegable que demuestre funcionalmente al menos uno de los tres
    componentes descritos.
- Una exposición ante los jurados explicando el problema abordado, las decisiones de
    diseño tomadas, la arquitectura de la solución y el impacto esperado.
- Evidencia del proceso de trabajo multidisciplinario del equipo.
_El alcance exacto de los entregables y los insumos que la Alcaldía de Medellín pondrá a
disposición de los equipos (datasets, documentación de procesos, acceso a información) serán
confirmados por la organización antes del inicio del evento.
Este documento es confidencial. Solo puede circular entre participantes activos del evento._


## 10. POTENCIAL DE IMPACTO Y ESCALA

La entidad aliada señaló que una solución funcional tiene un potencial de escalabilidad
significativo más allá de la Secretaría de Desarrollo Económico:

- Extensión a las otras 25 dependencias de la Alcaldía de Medellín, todas con el mismo
    problema estructural.
- Adopción por municipios descentralizados del departamento de Antioquia.
- Adaptación y comercialización para el sector privado, donde el mismo problema de
    gestión de solicitudes masivas existe con diferentes actores.
El problema abordado no es exclusivo del sector público. La gestión eficiente de solicitudes
masivas en lenguaje natural, con clasificación inteligente y síntesis automática, es un problema
que comparten organizaciones de cualquier tamaño y sector.
_Este documento es confidencial. Solo puede circular entre participantes activos del evento._


