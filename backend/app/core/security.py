import datetime
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
from backend.app.core.config import settings

# Use a stable, widely supported password hashing scheme for local/dev execution.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its hashed version."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash of the password."""
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: datetime.timedelta = None) -> str:
    """Generates a JWT access token for a given user identity."""
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
