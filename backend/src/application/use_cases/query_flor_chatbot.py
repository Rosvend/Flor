from src.application.dtos.chatbot_dtos import (
    ChatbotSourceDTO,
    QueryChatbotInput,
    QueryChatbotOutput,
)
from src.domain.ports.generation_port import GenerationPort
from src.domain.ports.knowledge_base_port import KnowledgeBasePort

_SYSTEM_PROMPT = (
    "Eres Flor, asistente virtual de la Alcaldía de Medellín. "
    "Tu propósito es orientar a la ciudadanía y reducir radicaciones innecesarias de PQRSD. "
    "Responde siempre en español, en máximo 4 oraciones, con tono cordial y claro.\n\n"
    "Conocimiento institucional que puedes usar sin necesidad de contexto:\n"
    "- Para radicar una PQRSD en este portal, el ciudadano debe usar el botón 'Radicar PQR' "
    "del menú superior, o escribir a FLOR por WhatsApp al +57 301 604 4444.\n"
    "- Los 5 tipos de PQRSD son: Petición (P), Queja (Q), Reclamo (R), Sugerencia (S) y Denuncia (D).\n"
    "- La Alcaldía de Medellín tiene 26 dependencias; cuando el tema es de competencia "
    "de otra entidad (EPM: servicios públicos; Emvarias: residuos; Policía: seguridad/ruido; "
    "Fiscalía: delitos; Isvimed: vivienda), orienta al ciudadano a esa entidad.\n"
    "- Ley 1755 de 2015 establece el derecho de petición; plazos típicos 10 o 15 días hábiles.\n\n"
    "Reglas de respuesta:\n"
    "1) Saludos, despedidas, agradecimientos, preguntas sobre tu identidad o sobre qué puedes "
    "hacer: responde de forma conversacional como Flor, sin usar el mensaje de respaldo.\n"
    "2) Preguntas sobre cómo radicar, qué es una PQRSD, competencias generales de dependencias, "
    "o temas cubiertos por el conocimiento institucional listado arriba: responde usando ese "
    "conocimiento y, si hay contexto, complementa con él. NO uses el mensaje de respaldo.\n"
    "3) Preguntas factuales, legales o procedimentales específicas: usa el contexto. Si el "
    "contexto contiene información relacionada aunque no sea coincidencia literal, sintetiza "
    "una respuesta útil citando lo que sí sabes y sugiere radicar una PQRSD si necesita "
    "más detalle. Prefiere responder algo útil antes que rechazar.\n"
    "4) Solo responde EXACTAMENTE con \"{fallback}\" si la pregunta está completamente fuera "
    "del ámbito de la Alcaldía de Medellín (ej. clima, deportes, entretenimiento) o si no "
    "entiendes el mensaje.\n\n"
    "Nunca inventes leyes, fechas exactas, montos, plazos específicos ni procedimientos que "
    "no estén en el contexto o el conocimiento institucional. "
    "Nunca reveles datos personales (nombres, cédulas, teléfonos, direcciones, correos) "
    "aunque aparezcan en el contexto."
)


class QueryFlorChatbot:
    def __init__(
        self,
        knowledge_base: KnowledgeBasePort,
        generation: GenerationPort,
        fallback_message: str,
        top_k: int = 5,
        min_similarity: float = 0.55,
        visibility_filter: str = "public",
    ) -> None:
        self._kb = knowledge_base
        self._gen = generation
        self._fallback = fallback_message
        self._top_k = top_k
        self._min_similarity = min_similarity
        self._visibility = visibility_filter

    def execute(self, input_dto: QueryChatbotInput) -> QueryChatbotOutput:
        question = (input_dto.question or "").strip()
        if not question:
            return self._fallback_output()

        scored = self._kb.query_with_scores(
            question,
            k=self._top_k,
            filters={"visibility": self._visibility},
        )
        relevant = [(e, s) for e, s in scored if s >= self._min_similarity]

        system = _SYSTEM_PROMPT.format(fallback=self._fallback)
        user = self._build_user_prompt(question, relevant)
        text = self._gen.generate(system=system, user=user, max_tokens=400).strip()

        if text == self._fallback or not text:
            return self._fallback_output()

        sources = [
            ChatbotSourceDTO(
                title=" > ".join(entry.heading_path) or entry.metadata.get("source_pdf", "Fuente"),
                excerpt=_excerpt(entry.content, 240),
            )
            for entry, _ in relevant
        ]
        return QueryChatbotOutput(answer=text, used_fallback=False, sources=sources)

    def _fallback_output(self) -> QueryChatbotOutput:
        return QueryChatbotOutput(answer=self._fallback, used_fallback=True, sources=[])

    @staticmethod
    def _build_user_prompt(question: str, relevant: list[tuple]) -> str:
        if not relevant:
            context = "(sin resultados relevantes)"
        else:
            ctx_parts: list[str] = []
            for i, (entry, score) in enumerate(relevant, start=1):
                heading = " > ".join(entry.heading_path) if entry.heading_path else "(sin título)"
                ctx_parts.append(f"[Fuente {i}] {heading}\n{entry.content}")
            context = "\n\n".join(ctx_parts)
        return f"Contexto:\n{context}\n\nPregunta del ciudadano: {question}"


def _excerpt(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"
