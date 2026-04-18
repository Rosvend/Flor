from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.auth.jwt_token_generator import JwtTokenGenerator
from src.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository

user_repository = InMemoryUserRepository()
password_hasher = BcryptPasswordHasher()
token_generator = JwtTokenGenerator()
