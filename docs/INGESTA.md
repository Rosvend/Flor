# Ingesta de PQRSD — Alcaldía de Medellín
### Canales: META + WhatsApp

---

## CANAL 1: META

### 1. Fuente de datos y acceso

- **Páginas fuente:** Una o varias páginas oficiales de la Alcaldía de Medellín en Meta (Facebook/Instagram)
- **Rol requerido:** Admin / Owner de cada página
- **Permisos necesarios:**
  - `pages_read_engagement`
  - `pages_show_list`
  - `pages_messaging` (para DMs)
- **Tipo de acceso:** Page Access Token por cada página administrada
- **App Review avanzado de Meta:** No requerido para este scope

---

### 2. Proceso de sincronización

- **Frecuencia:** Cada 24 horas (job programado)
- **Canales consumidos:**
  - DMs recibidos en las últimas 24 horas
  - Comentarios recibidos en las últimas 24 horas en **todos los posts existentes** de la página (no solo posts publicados en las últimas 24 horas)
- **Mecanismo:** Agente de sincronización via Graph API de Meta
  - Endpoint comentarios: `GET /{page-id}/feed?fields=comments{message,from,created_time}`
  - Endpoint DMs: `GET /me/conversations?fields=messages{message,from,created_time}`
  - Filtro temporal: `since` y `until` sobre `created_time` de las últimas 24 horas

---

### 3. Clasificación PQRSD

- Cada mensaje/comentario recuperado pasa por un clasificador
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
| Canal de origen | DM / Comentario | Siempre disponible |
| Contenido del mensaje | `message` | Siempre disponible |
| Fecha y hora | `created_time` | Siempre disponible |
| Post de origen | `post_id` | Solo en comentarios |

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
- Canal de origen (META_DM o META_COMMENT)

---

### 6. Envío al Datalake

Estructura del registro:

```json
{
  "radicado": "string",
  "timestamp_radicacion": "ISO8601",
  "tipo": "P | Q | R | S | D",
  "canal": "META_DM | META_COMMENT",
  "anonima": true | false,
  "usuario": {
    "nombre": "string | null",
    "id_meta": "string"
  },
  "contenido": "string",
  "metadata": {
    "post_id": "string | null",
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
| `metadata.post_id` | Solo comments | ❌ |
| `metadata.created_time` | ✅ | ✅ |