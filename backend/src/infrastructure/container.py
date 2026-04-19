import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno lo antes posible usando ruta absoluta
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages
from src.application.use_cases.ingest_knowledge_base_document import (
    IngestKnowledgeBaseDocument,
)
from src.application.use_cases.ingest_raw_messages import IngestRawMessages
from src.application.use_cases.query_flor_chatbot import QueryFlorChatbot
from src.application.use_cases.summarize_pqrsd import SummarizePQRSD
from src.application.use_cases.draft_response_pqrsd import DraftResponsePQRSD
from src.application.use_cases.ingest_email_pqrs import IngestEmailPQRS
from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
from src.infrastructure.knowledge_base.chroma_knowledge_base import ChromaKnowledgeBase
from src.infrastructure.knowledge_base.document_ingestion_service import (
    DocumentIngestionService,
)
from src.infrastructure.persistence.in_memory_raw_data_lake import InMemoryRawDataLake
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository

logger = logging.getLogger(__name__)

# ── Auth & Persistence ───────────────────────────────────────────────────────
if os.getenv("DATABASE_URL"):
    from src.infrastructure.persistence.database import init_db
    from src.infrastructure.persistence.postgres_user_repository import PostgresUserRepository
    try:
        logger.info("Conectando a base de datos PostgreSQL...")
        init_db()
        user_repository = PostgresUserRepository()
        logger.info("Conexión exitosa. Usando PostgresUserRepository.")
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        logger.warning("Fallo en la base de datos funcional. Cayendo en modo IN-MEMORY (VOLÁTIL) para permitir desarrollo.")
        from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
        user_repository = InMemoryUserRepository()
        # Seed user for development
        from src.domain.entities.user import User
        user_repository.save(User(
            id="admin-uuid",
            nombre="Admin Flor (Fallback)",
            correo_electronico="admin@flor.com",
            password_hash=BcryptPasswordHasher().hash("admin123"),
            organization_id=1
        ))
else:
    from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
    logger.warning("DATABASE_URL no configurada. Usando repositorio en memoria (VOLÁTIL)")
    user_repository = InMemoryUserRepository()
    # Seed user for development
    from src.domain.entities.user import User
    user_repository.save(User(
        id="admin-uuid",
        nombre="Admin Flor",
        correo_electronico="admin@flor.com",
        password_hash=BcryptPasswordHasher().hash("admin123"),
        organization_id=1
    ))
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

# ── Notificaciones (Gmail SMTP o no-op fallback) ─────────────────────────────
if os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD"):
    from src.infrastructure.notifications.gmail_smtp_adapter import GmailSMTPAdapter
    notifier = GmailSMTPAdapter()
    logger.info("Notificaciones via Gmail SMTP activadas.")
else:
    from src.domain.ports.notification_port import NotificationPort
    class _NoOpNotifier(NotificationPort):
        def notify_created(self, record: dict) -> None: pass
        def notify_resolved(self, record: dict) -> None: pass
    notifier = _NoOpNotifier()
    logger.warning("SMTP_HOST/SMTP_USER/SMTP_PASSWORD no configurados — notificaciones desactivadas.")

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
_pre_classifier = None

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

def _get_pre_classifier():
    global _pre_classifier
    if _pre_classifier is None:
        from src.infrastructure.classification.gemini_classification_adapter import GeminiClassificationAdapter
        _pre_classifier = GeminiClassificationAdapter()
    return _pre_classifier

def get_process_pqrs() -> ProcessPQRS:
    return ProcessPQRS(
        toxicity_detector=toxicity_detector,
        sentiment_analyzer=_get_sentiment_analyzer(),
        text_corrector=_get_text_corrector(),
        pre_classifier=_get_pre_classifier(),
    )

def get_migrate_raw_to_curated():
    from src.application.use_cases.migrate_raw_to_curated import MigrateRawToCurated
    return MigrateRawToCurated(
        raw_data_lake=raw_data_lake,
        curated_data_lake=curated_data_lake,
        classifier=_get_pre_classifier(),
        ingest_curated=ingest_curated_messages
    )


def get_draft_intelligent_response():
    from src.application.use_cases.draft_intelligent_response import DraftIntelligentResponse
    return DraftIntelligentResponse(
        curated_data_lake=curated_data_lake,
        similarity_analyzer=similarity_analyzer,
    )


cluster_pqrs = ClusterPQRS(
    similarity_analyzer=similarity_analyzer,
    data_lake=raw_data_lake,
)

# ── Email Ingestion (IMAP) ───────────────────────────────────────────────────
from src.infrastructure.connectors.imap_connector import ImapEmailConnector
email_connector = ImapEmailConnector()

def get_ingest_email_pqrs():
    return IngestEmailPQRS(
        email_connector=email_connector,
        process_pqrs=get_process_pqrs(),
        ingest_curated=ingest_curated_messages
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
summarize_pqrsd: SummarizePQRSD | None = None
draft_response_pqrsd: DraftResponsePQRSD | None = None
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
    summarize_pqrsd = SummarizePQRSD(generation=_generation)
    draft_response_pqrsd = DraftResponsePQRSD(
        knowledge_base=knowledge_base,
        generation=_generation,
        top_k=int(os.getenv("DRAFT_TOP_K", "6")),
        min_similarity=float(os.getenv("DRAFT_MIN_SIMILARITY", "0.55")),
    )
else:
    logger.warning("GEMINI_API_KEY not set — chatbot, summarize and draft endpoints will return 503.")
