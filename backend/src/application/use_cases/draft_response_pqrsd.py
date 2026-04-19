from src.application.dtos.pqrsd_assist_dtos import (
    DraftResponseInput,
    DraftResponseOutput,
    DraftSourceDTO,
)
from src.domain.ports.generation_port import GenerationPort
from src.domain.ports.knowledge_base_port import KnowledgeBasePort


_SYSTEM_PROMPT = (
    "Eres un asesor jurídico de la Alcaldía de Medellín. Tu tarea es redactar un "
    "borrador de respuesta formal a una PQRSD presentada por un ciudadano, usando "
    "EXCLUSIVAMENTE la información contenida en el contexto legal y normativo que "
    "se te entrega. Este borrador será revisado y aprobado por un asesor humano antes "
    "de enviarse al ciudadano.\n\n"
    "Estructura la respuesta así, siempre en español, tono cordial y formal:\n"
    "1. Saludo y referencia al radicado/asunto.\n"
    "2. Acuse de recibo breve de lo solicitado.\n"
    "3. Respuesta sustantiva basada en el contexto (cita artículo/ley cuando aparezca en el contexto).\n"
    "4. Próximos pasos o indicaciones de seguimiento si aplican.\n"
    "5. Despedida firmada como \"Alcaldía de Medellín\".\n\n"
    "Reglas estrictas:\n"
    "- No inventes leyes, fechas, montos, plazos, artículos ni procedimientos que no estén "
    "explícitamente en el contexto. Si no hay información suficiente, di que la solicitud "
    "será remitida a la dependencia competente y que el ciudadano recibirá respuesta dentro "
    "del plazo legal.\n"
    "- No reveles datos personales del ciudadano más allá de su nombre si se proporcionó.\n"
    "- Máximo 6 párrafos cortos. Español claro y accesible.\n"
    "- Este borrador NO es una respuesta oficial hasta que un asesor jurídico lo apruebe."
)


class DraftResponsePQRSD:
    def __init__(
        self,
        knowledge_base: KnowledgeBasePort,
        generation: GenerationPort,
        top_k: int = 6,
        min_similarity: float = 0.55,
        visibility_filter: str = "public",
        max_tokens: int = 700,
    ) -> None:
        self._kb = knowledge_base
        self._gen = generation
        self._top_k = top_k
        self._min_similarity = min_similarity
        self._visibility = visibility_filter
        self._max_tokens = max_tokens

    def execute(self, input_dto: DraftResponseInput) -> DraftResponseOutput:
        content = (input_dto.content or "").strip()
        if not content:
            return DraftResponseOutput(draft="", sources=[], used_fallback=True)

        # Retrieve KB chunks most relevant to the citizen's PQRSD body.
        scored = self._kb.query_with_scores(
            content,
            k=self._top_k,
            filters={"visibility": self._visibility},
        )
        relevant = [(e, s) for e, s in scored if s >= self._min_similarity]

        user_prompt = self._build_user_prompt(
            content=content,
            asunto=input_dto.asunto,
            citizen_name=input_dto.citizen_name,
            relevant=relevant,
        )

        draft = self._gen.generate(
            system=_SYSTEM_PROMPT,
            user=user_prompt,
            max_tokens=self._max_tokens,
        ).strip()

        if not draft:
            return DraftResponseOutput(draft="", sources=[], used_fallback=True)

        sources = [
            DraftSourceDTO(
                title=" > ".join(entry.heading_path) or entry.metadata.get("source_pdf", "Fuente"),
                excerpt=_excerpt(entry.content, 260),
            )
            for entry, _ in relevant
        ]
        return DraftResponseOutput(draft=draft, sources=sources, used_fallback=False)

    @staticmethod
    def _build_user_prompt(
        content: str,
        asunto: str | None,
        citizen_name: str | None,
        relevant: list[tuple],
    ) -> str:
        if relevant:
            ctx_parts: list[str] = []
            for i, (entry, _score) in enumerate(relevant, start=1):
                heading = " > ".join(entry.heading_path) if entry.heading_path else "(sin título)"
                ctx_parts.append(f"[Fuente {i}] {heading}\n{entry.content}")
            context = "\n\n".join(ctx_parts)
        else:
            context = "(sin resultados relevantes)"

        sections = [f"Contexto legal y normativo (usa solo esta información):\n{context}"]
        if asunto:
            sections.append(f"Asunto/Tipo: {asunto}")
        if citizen_name:
            sections.append(f"Ciudadano: {citizen_name}")
        sections.append(f"PQRSD del ciudadano:\n{content}")
        sections.append("Redacta el borrador de respuesta formal.")
        return "\n\n".join(sections)


def _excerpt(text: str, max_chars: int) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"
