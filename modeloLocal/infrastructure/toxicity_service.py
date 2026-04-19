import re

# Lista de groserías y expresiones ofensivas comunes en español (Colombia/Latam)
OFFENSIVE_WORDS = [
    # Insultos directos
    r"\bhijueputa\b", r"\bhp\b", r"\bmalparido\b", r"\bmalparida\b",
    r"\bgonorrea\b", r"\bmarica\b", r"\bimbécil\b", r"\bimbecil\b",
    r"\bestúpid[oa]\b", r"\bestupid[oa]\b", r"\bidiot[ae]?\b",
    r"\binútil(?:es)?\b", r"\binutiles\b", r"\bpendej[oa]\b",
    r"\bbob[oa]\b", r"\bbrut[oa]\b", r"\btarad[oa]\b",
    # Groserías
    r"\bmierda\b", r"\bcarajo\b", r"\bculo\b", r"\bput[oa]\b",
    r"\bverga\b", r"\bjoder\b", r"\bjodid[oa]\b", r"\bcoño\b",
    r"\bchinga\b", r"\bcabr[oó]n\b", r"\bporquería\b", r"\bporqueria\b",
    r"\basquer[oa]s[oa]\b", r"\bbasura\b",
    # Expresiones compuestas
    r"\bhijo de\b.*\bputa\b", r"\bváyanse al\b.*\bcarajo\b",
    r"\bno sirven para\b.*\bnada\b",
    # Amenazas
    r"\blos voy a\b", r"\bme las van a pagar\b", r"\bse van a arrepentir\b",
]

class ToxicityService:
    def __init__(self):
        # Compilar patrones una sola vez para mejor rendimiento
        self.patterns = [re.compile(p, re.IGNORECASE) for p in OFFENSIVE_WORDS]

    def analyze(self, text: str) -> dict:
        found_words = []
        
        for pattern in self.patterns:
            matches = pattern.findall(text)
            if matches:
                found_words.extend(matches)
        
        is_offensive = len(found_words) > 0
        
        return {
            "is_offensive": is_offensive,
            "offensive_words_found": list(set(found_words)),
            "confidence": 1.0 if is_offensive else 0.0,
            "warning": (
                "⚠️ ALERTA: El texto contiene lenguaje irrespetuoso u ofensivo. "
                "Según el Art. 19 de la Ley 1755/2015, las peticiones irrespetuosas "
                "pueden ser rechazadas por la entidad."
            ) if is_offensive else None
        }
