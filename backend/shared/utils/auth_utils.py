from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import bcrypt
import os
import asyncio

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

def verify_password(plain_password, hashed_password):
    """Synchronous password verification (fast, used in sync contexts)."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def get_password_hash(password):
    """Synchronous hash - use work factor 10 to avoid blocking event loop too long."""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=10)
    ).decode('utf-8')

async def async_get_password_hash(password):
    """Async-safe password hashing - runs bcrypt in thread pool to avoid blocking."""
    return await asyncio.to_thread(get_password_hash, password)

async def async_verify_password(plain_password, hashed_password):
    """Async-safe password verification - runs in thread pool."""
    return await asyncio.to_thread(verify_password, plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

import logging

logger = logging.getLogger(__name__)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token payload missing 'sub' claim")
            return None
        return email
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except JWTError as e:
        logger.warning(f"JWT verification error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None
