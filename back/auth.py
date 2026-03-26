from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
import models
import hashlib
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

# NOTE: passlib+bcrypt is currently incompatible with the installed bcrypt backend
# in this environment (it raises on >72-byte secrets during backend self-check).
# Using PBKDF2 avoids bcrypt backend issues on Windows and is sufficient for this app.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer()


def _prehash(plain: str) -> str:
    digest = hashlib.sha256(plain.encode()).digest()
    return base64.b64encode(digest).decode()


def hash_password(plain: str) -> str:
    return pwd_context.hash(_prehash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prehash(plain), hashed)


def create_access_token(user_id: int, role: Literal["driver", "disabled"]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependency: get current user (driver or disabled) ────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    user_id = int(payload["sub"])
    role = payload["role"]

    if role == "driver":
        user = db.query(models.Driver).filter(models.Driver.id == user_id).first()
    else:
        user = db.query(models.Disabled).filter(models.Disabled.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user.role = role  # attach role so callers can inspect it
    return user


def require_driver(user=Depends(get_current_user)):
    if user.role != "driver":
        raise HTTPException(status_code=403, detail="Drivers only")
    return user


def require_disabled(user=Depends(get_current_user)):
    if user.role != "disabled":
        raise HTTPException(status_code=403, detail="Disabled users only")
    return user