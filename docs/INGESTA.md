# Ingesta de PQRSD — Alcaldía de Medellín
### Canales: META + WhatsApp

---

## CANAL 1: META

> ⚠️ **Alcance real (Hackathon):** Por limitaciones de permisos disponibles en modo desarrollo sin App Review de Meta, el alcance actual cubre únicamente **DMs de Facebook**. Comentarios de posts e Instagram quedan fuera del alcance de esta implementación. El diseño ideal está documentado como referencia para una implementación futura con permisos completos.

### 1. Fuente de datos y acceso

- **Páginas fuente:** Una o varias páginas oficiales de la Alcaldía de Medellín en Facebook
- **Rol requerido:** Admin / Owner de cada página
- **Permisos disponibles (modo desarrollo):**
  - `pages_show_list` ✅
  - `pages_messaging` ✅ (habilita lectura de DMs)
- **Permisos requeridos para alcance completo (requieren App Review):**
  - `pages_read_engagement` — comentarios de posts
  - `instagram_basic` — contenido de Instagram
  - `instagram_manage_messages` — DMs de Instagram
- **Tipo de acceso:** Page Access Token por cada página administrada

---

### 2. Proceso de sincronización

- **Frecuencia:** Cada 24 horas (job programado)
- **Canales consumidos (alcance actual):**
  - DMs recibidos en las últimas 24 horas en páginas de Facebook administradas
- **Canales pendientes (alcance futuro):**
  - Comentarios en todos los posts de las últimas 24 horas
  - DMs y comentarios de Instagram
- **Mecanismo:** Agente de sincronización via Graph API de Meta
  - Endpoint DMs: `GET /{page-id}/conversations?fields=messages{message,from,created_time}`
  - Filtro temporal: `since` y `until` sobre `created_time` de las últimas 24 horas

---

### 3. Clasificación PQRSD

- Cada DM recuperado pasa por un clasificador
- El clasificador determina si el contenido corresponde a una **Pregunta, Queja, Reclamo, Sugerencia o Duda**
- Los mensajes que no sean PQRSD se descartan
- Los mensajes clasificados como PQRSD avanzan al siguiente paso

---

### 4. Extracción de datos del usuario

Por cada PQRSD identificada se extrae:

| Campo | Fuente | Disponibilidad |
|---|---|---|
| Nombre del usuario | Perfil Meta (`from.name`) | Cuando es público |
| ID de usuario Meta | `from.id` | Siempre disponible |
| Canal de origen | DM Facebook | Siempre disponible |
| Contenido del mensaje | `message` | Siempre disponible |
| Fecha y hora | `created_time` | Siempre disponible |

---

### 5. Radicación

Se evalúa si la PQRSD tiene información suficiente para personalizarla:

```
¿Tiene nombre + contenido claro?
    ├── SÍ → Se radica como PQRSD personalizada (asociada al ciudadano)
    └── NO → Se radica como PQRSD anónima
```

Ambos tipos reciben:
- Número de radicado
- Timestamp de radicación
- Clasificación del tipo (P / Q / R / S / D)
- Canal de origen (META_DM)

---

### 6. Envío al Datalake

Estructura del registro:

```json
{
  "radicado": "string",
  "timestamp_radicacion": "ISO8601",
  "tipo": "P | Q | R | S | D",
  "canal": "META_DM",
  "anonima": true | false,
  "usuario": {
    "nombre": "string | null",
    "id_meta": "string"
  },
  "contenido": "string",
  "metadata": {
    "created_time": "ISO8601"
  }
}
```

---
---

## CANAL 2: WHATSAPP (FLOR)

### 1. Fuente de datos y acceso

- **Plataforma:** FLOR — chatbot oficial de la Alcaldía de Medellín
- **Canal:** WhatsApp Business (número oficial de la Alcaldía)
- **Acceso:** Dominio total sobre FLOR y el número de WhatsApp Business
- **Tipo de ingesta:** Tiempo real — el ciudadano inicia el flujo activamente

---

### 2. Flujo del ciudadano

El ciudadano navega por el menú de FLOR hasta seleccionar la opción de radicar PQRSD. A partir de ahí el chatbot recolecta los datos de forma estructurada:

```
FLOR
 └── Opción: Radicar PQRSD
      ├── Tipo: P / Q / R / S / D
      ├── Nombre del ciudadano
      ├── Número de documento (opcional)
      ├── Descripción del caso
      └── Confirmación → Envío
```

A diferencia de META, **no hay clasificador**: el ciudadano ya eligió radicar una PQRSD explícitamente y el tipo fue seleccionado en el flujo. No hay mensajes que descartar.

---

### 3. Radicación

Al confirmar el envío, FLOR envía los datos estructurados al backend:

- Todos los campos recolectados en el flujo llegan completos
- Si el ciudadano proporcionó nombre y/o documento → PQRSD **personalizada**
- Si el ciudadano omitió datos de identificación → PQRSD **anónima**

Ambos tipos reciben:
- Número de radicado
- Timestamp de radicación
- Clasificación del tipo (P / Q / R / S / D)
- Canal de origen (WHATSAPP)

FLOR confirma el radicado al ciudadano en el chat con el número de radicado generado.

---

### 4. Envío al Datalake

Estructura del registro:

```json
{
  "radicado": "string",
  "timestamp_radicacion": "ISO8601",
  "tipo": "P | Q | R | S | D",
  "canal": "WHATSAPP",
  "anonima": true | false,
  "usuario": {
    "nombre": "string | null",
    "documento": "string | null",
    "telefono": "string"
  },
  "contenido": "string",
  "metadata": {
    "created_time": "ISO8601"
  }
}
```

---
---

## Estructura unificada del Datalake

Ambos canales convergen en la misma entidad con campos comunes y campos opcionales por canal:

| Campo | META | WhatsApp |
|---|---|---|
| `radicado` | ✅ | ✅ |
| `timestamp_radicacion` | ✅ | ✅ |
| `tipo` | ✅ | ✅ |
| `canal` | ✅ | ✅ |
| `anonima` | ✅ | ✅ |
| `contenido` | ✅ | ✅ |
| `usuario.nombre` | Opcional | Opcional |
| `usuario.id_meta` | ✅ | ❌ |
| `usuario.documento` | ❌ | Opcional |
| `usuario.telefono` | ❌ | ✅ |
| `metadata.post_id` | ❌ (futuro) | ❌ |
| `metadata.created_time` | ✅ | ✅ |