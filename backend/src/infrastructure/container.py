import os

from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.in_memory_raw_data_lake import InMemoryRawDataLake
from src.application.use_cases.ingest_raw_messages import IngestRawMessages
from src.application.use_cases.ingest_curated_messages import IngestCuratedMessages

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
