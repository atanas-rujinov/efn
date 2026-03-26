from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Driver ──────────────────────────────────────────────────────────────────

class DriverBase(BaseModel):
    email: str
    name: str
    password: str

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

class DriverOut(BaseModel):
    id: int
    created_at: datetime
    email: str
    name: str

    model_config = {"from_attributes": True}


# ── Disabled ─────────────────────────────────────────────────────────────────

class DisabledBase(BaseModel):
    email: str
    name: str
    password: str
    disability: str

class DisabledCreate(DisabledBase):
    pass

class DisabledUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    disability: Optional[str] = None

class DisabledOut(BaseModel):
    id: int
    created_at: datetime
    email: str
    name: str
    disability: str

    model_config = {"from_attributes": True}


# ── Car ──────────────────────────────────────────────────────────────────────

class CarBase(BaseModel):
    model: str
    color: str
    plate: str
    driver: int

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    model: Optional[str] = None
    color: Optional[str] = None
    plate: Optional[str] = None
    driver: Optional[int] = None

class CarOut(BaseModel):
    id: int
    model: str
    color: str
    plate: str
    driver: int

    model_config = {"from_attributes": True}


# ── Drive Request ────────────────────────────────────────────────────────────

class DriveRequestBase(BaseModel):
    description: str
    start_address: str
    start_lat: float
    start_lon: float
    dest_address: str
    dest_lat: float
    dest_lon: float
    is_completed: bool = False
    
    # FIX: These are now Optional so the frontend isn't forced to send them
    driver: Optional[int] = None
    disabled: Optional[int] = None

class DriveRequestCreate(DriveRequestBase):
    pass

class DriveRequestUpdate(BaseModel):
    description: Optional[str] = None
    start_address: Optional[str] = None
    start_lat: Optional[float] = None
    start_lon: Optional[float] = None
    dest_address: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None
    is_completed: Optional[bool] = None
    driver: Optional[int] = None
    disabled: Optional[int] = None

class DriveRequestOut(BaseModel):
    id: int
    created_at: datetime
    description: str
    start_address: str
    start_lat: float
    start_lon: float
    dest_address: str
    dest_lat: float
    dest_lon: float
    is_completed: bool
    
    # FIX: Allow driver out to be None/null in JSON 
    driver: Optional[int] = None
    disabled: int

    model_config = {"from_attributes": True}


# ── Shop Request ─────────────────────────────────────────────────────────────

class ShopRequestBase(BaseModel):
    description: str
    start_address: str
    start_lat: float
    start_lon: float
    dest_address: str
    dest_lat: float
    dest_lon: float
    is_completed: bool = False
    
    # FIX: Same optional handling as DriveRequests
    driver: Optional[int] = None
    disabled: Optional[int] = None

class ShopRequestCreate(ShopRequestBase):
    pass

class ShopRequestUpdate(BaseModel):
    description: Optional[str] = None
    start_address: Optional[str] = None
    start_lat: Optional[float] = None
    start_lon: Optional[float] = None
    dest_address: Optional[str] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None
    is_completed: Optional[bool] = None
    driver: Optional[int] = None
    disabled: Optional[int] = None

class ShopRequestOut(BaseModel):
    id: int
    created_at: datetime
    description: str
    start_address: str
    start_lat: float
    start_lon: float
    dest_address: str
    dest_lat: float
    dest_lon: float
    is_completed: bool
    driver: Optional[int] = None
    disabled: int

    model_config = {"from_attributes": True}


# ── Review ───────────────────────────────────────────────────────────────────

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None
    driver: int
    author: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    driver: Optional[int] = None
    author: Optional[int] = None

class ReviewOut(BaseModel):
    id: int
    created_at: datetime
    rating: int
    comment: Optional[str] = None
    driver: int
    author: int

    model_config = {"from_attributes": True}