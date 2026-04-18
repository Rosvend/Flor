# Ingesta de PQRSD desde META — Alcaldía de Medellín

## 1. Fuente de datos y acceso

- **Páginas fuente:** Una o varias páginas oficiales de la Alcaldía de Medellín en Meta (Facebook/Instagram)
- **Rol requerido:** Admin / Owner de cada página
- **Permisos necesarios:**
  - `pages_read_engagement`
  - `pages_show_list`
  - `pages_messaging` (para DMs)
- **Tipo de acceso:** Page Access Token por cada página administrada
- **App Review avanzado de Meta:** No requerido para este scope

---

## 2. Proceso de sincronización

- **Frecuencia:** Cada 24 horas (job programado)
- **Canales consumidos:**
  - DMs recibidos en las últimas 24 horas
  - Comentarios recibidos en las últimas 24 horas en **todos los posts existentes** de la página (no solo posts publicados en las últimas 24 horas)
- **Mecanismo:** Agente de sincronización via Graph API de Meta
  - Endpoint comentarios: `GET /{page-id}/feed?fields=comments{message,from,created_time}`
  - Endpoint DMs: `GET /me/conversations?fields=messages{message,from,created_time}`
  - Filtro temporal: `since` y `until` sobre `created_time` de las últimas 24 horas

---

## 3. Clasificación PQRSD

- Cada mensaje/comentario recuperado pasa por un clasificador
- El clasificador determina si el contenido corresponde a una **Pregunta, Queja, Reclamo, Sugerencia o Duda**
- Los mensajes que no sean PQRSD se descartan
- Los mensajes clasificados como PQRSD avanzan al siguiente paso

---

## 4. Extracción de datos del usuario

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

## 5. Radicación

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
- Canal de origen (META — DM o META — Comentario)

---

## 6. Envío al Datalake

- Una vez radicada, cada PQRSD se envía al datalake
- Estructura mínima del registro:

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