import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


class InvalidTokenError(Exception):
    pass


class JwtTokenGenerator:
    def __init__(self) -> None:
        self._secret = os.getenv("JWT_SECRET", "changeme-set-a-real-secret-in-env")
        self._algorithm = "HS256"
        self._expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    def generate(self, payload: dict) -> str:
        data = payload.copy()
        data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        return jwt.encode(data, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as e:
            raise InvalidTokenError(str(e)) from e
