from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.config import settings

MAX_BCRYPT_PASSWORD_BYTES = 72


def password_exceeds_bcrypt_limit(password: str) -> bool:
    """Bcrypt only accepts the first 72 UTF-8 bytes of a password."""
    return len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES


def hash_password(password: str) -> str:
    if password_exceeds_bcrypt_limit(password):
        raise ValueError("Password must not exceed 72 UTF-8 bytes")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if password_exceeds_bcrypt_limit(plain):
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (TypeError, ValueError):
        return False


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
