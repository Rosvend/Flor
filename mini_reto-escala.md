### 1. Latencia y Throughput del Pipeline Asíncrono (Rendimiento Técnico)
Esta métrica evalúa la capacidad del sistema para absorber picos masivos de ciudadanos radicando PQRS (ej. tras una emergencia en la ciudad) sin que la plataforma se caiga ni el frontend se congele.
*   **Métrica a medir:** Volumen de PQRS procesadas por hora y Tiempo de ejecución en segundo plano (< 3 segundos por documento procesado por YOLO y Gemini).
*   **Rol Asociado:** **Ingeniero Cloud / DevOps (o Arquitecto Backend).**
*   **Responsabilidades:** 
    *   Garantizar que el procesamiento de IA pesada se mantenga en *Background Tasks* (como lo implementamos).
    *   Configurar el auto-escalado de los servidores (ej. subir más instancias de FastAPI/Uvicorn si la CPU llega al 80%).
    *   Monitorear y manejar los límites de cuota (Rate Limits) de la API de Google Gemini y el S3 Data Lake.

### 2. Tasa de Aprobación de Borradores y Precisión de Enrutamiento (Rendimiento Operativo)
La IA no es escalable si los trabajadores tienen que borrar y reescribir todo lo que la IA sugiere. Esta métrica mide el impacto real del modelo en la productividad del funcionario.
*   **Métrica a medir:** Porcentaje de borradores generados por la IA que los funcionarios envían sin hacerle ediciones mayores (Ideal: > 75%), y porcentaje de PQRS asignadas correctamente a la secretaría correspondiente.
*   **Rol Asociado:** **Analista de IA / Prompt Engineer.**
*   **Responsabilidades:**
    *   Revisar periódicamente los casos donde la IA se equivocó de Secretaría (Falsos Positivos).
    *   Afinar y optimizar las instrucciones (Prompts) en el código fuente basándose en la retroalimentación de los trabajadores.
    *   Mantener actualizada la base de conocimiento vectorial (los PDFs de precedentes) para que el modelo siga siendo preciso con las nuevas normativas.

### 3. Eficiencia de Costos Computacionales por PQRS (Rendimiento Financiero)
Una arquitectura de IA escalable debe ser económicamente sostenible. Procesar imágenes con YOLO y textos con LLMs cuesta dinero o recursos de máquina.
*   **Métrica a medir:** Costo promedio en "tokens de LLM" y almacenamiento (S3) por cada PQRS radicada, así como la tasa de "Acierto de Caché" (Cache Hit Ratio).
*   **Rol Asociado:** **Product Manager / Tech Lead.**
*   **Responsabilidades:**
    *   Definir y auditar estrategias de ahorro, como el uso de memorias caché (ej. la caché de 24 horas que hicimos para el mapa de densidad) para evitar llamadas innecesarias a la API.
    *   Decidir cuándo usar modelos rápidos y económicos (Gemini 2.5 Flash) frente a modelos más lentos y costosos, dependiendo de la complejidad de la queja.
    *   Gestionar el ciclo de vida de los datos (ej. mover imágenes antiguas de S3 a un almacenamiento más barato a los 6 meses).

---

Con estas tres métricas cubres los tres pilares de cualquier arquitectura escalable moderna: **Servidores (Cloud), Precisión del Algoritmo (IA), y Viabilidad Económica (Negocio).**