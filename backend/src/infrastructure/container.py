from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.persistence.s3_raw_data_lake import S3RawDataLake
from src.application.use_cases.ingest_raw_messages import IngestRawMessages

user_repository = InMemoryUserRepository()
password_hasher = BcryptPasswordHasher()
token_generator = JwtTokenGenerator()

raw_data_lake = S3RawDataLake()
ingest_raw_messages = IngestRawMessages(data_lake=raw_data_lake)
