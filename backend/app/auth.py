from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    # Ensure sub is a string (python-jose requirement)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": datetime.utcnow() + expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except Exception:
        return None
