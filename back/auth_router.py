from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal, Optional

from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user
import models

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: str
    phone: str  # Added to capture phone number from frontend
    password: str
    role: Literal["driver", "disabled"]
    disability: Optional[str] = None  # required when role == "disabled"


class LoginRequest(BaseModel):
    email: str
    password: str
    role: Literal["driver", "disabled"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    disability: Optional[str] = None


# ── POST /auth/signup ─────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if payload.role == "driver":
        existing = db.query(models.Driver).filter(models.Driver.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Added phone=payload.phone to save it to the Driver model
        user = models.Driver(
            email=payload.email,
            name=payload.name,
            phone=payload.phone,
            password=hash_password(payload.password),
        )
    else:
        if not payload.disability:
            raise HTTPException(status_code=422, detail="disability field is required for disabled users")
        
        existing = db.query(models.Disabled).filter(models.Disabled.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Added phone=payload.phone to save it to the Disabled model
        user = models.Disabled(
            email=payload.email,
            name=payload.name,
            phone=payload.phone,
            password=hash_password(payload.password),
            disability=payload.disability,
        )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, payload.role)
    return TokenResponse(access_token=token)


# ── POST /auth/login ──────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    if payload.role == "driver":
        user = db.query(models.Driver).filter(models.Driver.email == payload.email).first()
    else:
        user = db.query(models.Disabled).filter(models.Disabled.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, payload.role)
    return TokenResponse(access_token=token)


# ── GET /auth/me ──────────────────────────────────────────────────────────────

@router.get("/me", response_model=MeResponse)
def me(current_user=Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        phone=getattr(current_user, 'phone', None),
        disability=getattr(current_user, 'disability', None),
    )