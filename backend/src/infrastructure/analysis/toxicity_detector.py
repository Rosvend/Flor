import re

from src.domain.ports.pqrs_analyzer_port import ToxicityDetectorPort

# Groserías y expresiones ofensivas en español (Colombia/Latam)
OFFENSIVE_PATTERNS = [
    r"\bhijueputa\b", r"\bhp\b", r"\bmalparido\b", r"\bmalparida\b",
    r"\bgonorrea\b", r"\bmarica\b", r"\bimbécil\b", r"\bimbecil\b",
    r"\bestúpid[oa]\b", r"\bestupid[oa]\b", r"\bidiot[ae]?\b",
    r"\binútil(?:es)?\b", r"\binutiles\b", r"\bpendej[oa]\b",
    r"\bbob[oa]\b", r"\bbrut[oa]\b", r"\btarad[oa]\b",
    r"\bmierda\b", r"\bcarajo\b", r"\bculo\b", r"\bput[oa]\b",
    r"\bverga\b", r"\bjoder\b", r"\bjodid[oa]\b", r"\bcoño\b",
    r"\bchinga\b", r"\bcabr[oó]n\b", r"\bporquería\b", r"\bporqueria\b",
    r"\basquer[oa]s[oa]\b", r"\bbasura\b",
    r"\bhijo de\b.*\bputa\b", r"\bváyanse al\b.*\bcarajo\b",
    r"\blos voy a\b", r"\bme las van a pagar\b", r"\bse van a arrepentir\b",
]


class RegexToxicityDetector(ToxicityDetectorPort):
    """Detección de lenguaje ofensivo basada en regex."""

    def __init__(self) -> None:
        self._patterns = [re.compile(p, re.IGNORECASE) for p in OFFENSIVE_PATTERNS]

    def analyze(self, text: str) -> dict:
        found: list[str] = []
        for pattern in self._patterns:
            matches = pattern.findall(text)
            if matches:
                found.extend(matches)

        is_offensive = len(found) > 0
        return {
            "is_offensive": is_offensive,
            "offensive_words_found": list(set(found)),
            "confidence": 1.0 if is_offensive else 0.0,
            "warning": (
                "⚠️ ALERTA: El texto contiene lenguaje irrespetuoso u ofensivo. "
                "Según el Art. 19 de la Ley 1755/2015, las peticiones irrespetuosas "
                "pueden ser rechazadas por la entidad."
            ) if is_offensive else None,
        }
