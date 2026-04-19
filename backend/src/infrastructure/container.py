import os

from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.in_memory_raw_data_lake import InMemoryRawDataLake
from src.application.use_cases.ingest_raw_messages import IngestRawMessages
from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages

# ── Auth & Persistence ───────────────────────────────────────────────────────
user_repository = InMemoryUserRepository()
password_hasher = BcryptPasswordHasher()
token_generator = JwtTokenGenerator()

if os.getenv("S3_RAW_BUCKET"):
    from src.infrastructure.persistence.s3_raw_data_lake import S3RawDataLake
    from src.infrastructure.persistence.s3_curated_data_lake import S3CuratedDataLake
    raw_data_lake = S3RawDataLake()
    curated_data_lake = S3CuratedDataLake()
else:
    from src.infrastructure.persistence.in_memory_curated_data_lake import InMemoryCuratedDataLake
    raw_data_lake = InMemoryRawDataLake()
    curated_data_lake = InMemoryCuratedDataLake()

ingest_raw_messages = IngestRawMessages(data_lake=raw_data_lake)
ingest_curated_messages = IngestCuratedMessages(data_lake=curated_data_lake)

# ── PQRS Analysis ────────────────────────────────────────────────────────────
from src.infrastructure.analysis.toxicity_detector import RegexToxicityDetector
from src.infrastructure.analysis.similarity_analyzer import TfidfSimilarityAnalyzer
from src.application.use_cases.process_pqrs import ProcessPQRS
from src.application.use_cases.cluster_pqrs import ClusterPQRS

toxicity_detector = RegexToxicityDetector()
similarity_analyzer = TfidfSimilarityAnalyzer()

# Sentiment & Corrector se cargan bajo demanda (modelos pesados)
_sentiment_analyzer = None
_text_corrector = None


def _get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        from src.infrastructure.analysis.sentiment_analyzer import BetoSentimentAnalyzer
        _sentiment_analyzer = BetoSentimentAnalyzer()
    return _sentiment_analyzer


def _get_text_corrector():
    global _text_corrector
    if _text_corrector is None:
        from src.infrastructure.analysis.text_corrector import GeminiTextCorrector
        _text_corrector = GeminiTextCorrector()
    return _text_corrector


def get_process_pqrs() -> ProcessPQRS:
    return ProcessPQRS(
        toxicity_detector=toxicity_detector,
        sentiment_analyzer=_get_sentiment_analyzer(),
        text_corrector=_get_text_corrector(),
    )


cluster_pqrs = ClusterPQRS(
    similarity_analyzer=similarity_analyzer,
    data_lake=raw_data_lake,
)
