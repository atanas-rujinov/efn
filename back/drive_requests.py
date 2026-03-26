from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

# FIX: Import the auth dependency
from auth import require_disabled 

router = APIRouter(prefix="/drive-requests", tags=["Drive Requests"])


@router.get("/", response_model=List[schemas.DriveRequestOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.DriveRequest).all()


@router.get("/{id}", response_model=schemas.DriveRequestOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.DriveRequest).filter(models.DriveRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Drive request not found")
    return record


@router.post("/", response_model=schemas.DriveRequestOut, status_code=201)
def create(
    payload: schemas.DriveRequestCreate, 
    db: Session = Depends(get_db),
    # FIX: Require authentication and get the logged in user
    current_user = Depends(require_disabled) 
):
    # FIX: Convert payload to dict and inject the author's ID automatically
    data = payload.model_dump()
    data["disabled"] = current_user.id 
    
    # Driver will naturally be None since it was left out of the frontend payload

    record = models.DriveRequest(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{id}", response_model=schemas.DriveRequestOut)
def update(id: int, payload: schemas.DriveRequestUpdate, db: Session = Depends(get_db)):
    record = db.query(models.DriveRequest).filter(models.DriveRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Drive request not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    record = db.query(models.DriveRequest).filter(models.DriveRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Drive request not found")
    db.delete(record)
    db.commit()