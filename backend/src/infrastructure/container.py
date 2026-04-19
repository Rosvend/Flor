import logging
import os
from pathlib import Path

from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages
from src.application.use_cases.ingest_knowledge_base_document import (
    IngestKnowledgeBaseDocument,
)
from src.application.use_cases.ingest_raw_messages import IngestRawMessages
from src.application.use_cases.query_flor_chatbot import QueryFlorChatbot
from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
from src.infrastructure.knowledge_base.chroma_knowledge_base import ChromaKnowledgeBase
from src.infrastructure.knowledge_base.document_ingestion_service import (
    DocumentIngestionService,
)
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
from src.infrastructure.persistence.in_memory_raw_data_lake import InMemoryRawDataLake
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository

logger = logging.getLogger(__name__)

# ── Auth & Persistence ───────────────────────────────────────────────────────
if os.getenv("DATABASE_URL"):
    from src.infrastructure.persistence.database import init_db
    from src.infrastructure.persistence.postgres_user_repository import PostgresUserRepository
    init_db()
    user_repository = PostgresUserRepository()
else:
    from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
    user_repository = InMemoryUserRepository()
password_hasher = BcryptPasswordHasher()
token_generator = JwtTokenGenerator()

# ── Data lake (S3 or in-memory fallback) ────────────────────────────────────
if os.getenv("S3_RAW_BUCKET"):
    from src.infrastructure.persistence.s3_curated_data_lake import S3CuratedDataLake
    from src.infrastructure.persistence.s3_raw_data_lake import S3RawDataLake
    raw_data_lake = S3RawDataLake()
    curated_data_lake = S3CuratedDataLake()
else:
    from src.infrastructure.persistence.in_memory_curated_data_lake import (
        InMemoryCuratedDataLake,
    )
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
_classifier = None
_router = None
_department_repo = None


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


def _get_classifier():
    global _classifier
    if _classifier is None:
        from src.infrastructure.analysis.zero_shot_classifier import HuggingFaceZeroShotClassifier
        _classifier = HuggingFaceZeroShotClassifier()
    return _classifier


def _get_router():
    global _router
    global _department_repo
    if _router is None:
        from src.infrastructure.knowledge_base.json_department_repository import JsonDepartmentRepository
        from src.infrastructure.analysis.semantic_router import SemanticDepartmentRouter

        if _department_repo is None:
            seed_path = Path(__file__).parent / "knowledge_base" / "data" / "departments.json"
            _department_repo = JsonDepartmentRepository(seed_path)

        _router = SemanticDepartmentRouter(repository=_department_repo)
    return _router


def get_process_pqrs() -> ProcessPQRS:
    return ProcessPQRS(
        toxicity_detector=toxicity_detector,
        sentiment_analyzer=_get_sentiment_analyzer(),
        text_corrector=_get_text_corrector(),
        classifier=_get_classifier(),
        router=_get_router(),
    )


cluster_pqrs = ClusterPQRS(
    similarity_analyzer=similarity_analyzer,
    data_lake=raw_data_lake,
)

# ── Chatbot (F7) ────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CHROMA_DIR = _REPO_ROOT / "backend" / ".knowledge_base" / "chroma"
_UPLOADS_DIR = _REPO_ROOT / "backend" / ".knowledge_base" / "uploads"
_MARKDOWN_DIR = _REPO_ROOT / "docs" / "knowledge_base"

knowledge_base = ChromaKnowledgeBase(persist_dir=_CHROMA_DIR)

document_ingestion_service = DocumentIngestionService(
    knowledge_base=knowledge_base,
    uploads_dir=_UPLOADS_DIR,
    markdown_dir=_MARKDOWN_DIR,
)

ingest_knowledge_base_document = IngestKnowledgeBaseDocument(
    ingestion=document_ingestion_service,
)

query_flor_chatbot: QueryFlorChatbot | None = None
if os.getenv("GEMINI_API_KEY"):
    from src.infrastructure.classification.gemini_generation_adapter import (
        GeminiGenerationAdapter,
    )
    _generation = GeminiGenerationAdapter()
    query_flor_chatbot = QueryFlorChatbot(
        knowledge_base=knowledge_base,
        generation=_generation,
        fallback_message=os.getenv(
            "CHATBOT_FALLBACK_MESSAGE",
            "No tengo esa respuesta. Puedes radicar un PQRSD o escribir a FLOR por WhatsApp al +57 301 604 4444.",
        ),
        top_k=int(os.getenv("CHATBOT_TOP_K", "5")),
        min_similarity=float(os.getenv("CHATBOT_MIN_SIMILARITY", "0.55")),
    )
else:
    logger.warning("GEMINI_API_KEY not set — chatbot endpoint will return 503.")
