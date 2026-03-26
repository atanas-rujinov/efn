from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter(prefix="/disabled", tags=["Disabled"])


@router.get("/", response_model=List[schemas.DisabledOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Disabled).all()


@router.get("/{id}", response_model=schemas.DisabledOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.Disabled).filter(models.Disabled.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Disabled user not found")
    return record


@router.post("/", response_model=schemas.DisabledOut, status_code=201)
def create(payload: schemas.DisabledCreate, db: Session = Depends(get_db)):
    record = models.Disabled(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{id}", response_model=schemas.DisabledOut)
def update(id: int, payload: schemas.DisabledUpdate, db: Session = Depends(get_db)):
    record = db.query(models.Disabled).filter(models.Disabled.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Disabled user not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    record = db.query(models.Disabled).filter(models.Disabled.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Disabled user not found")
    db.delete(record)
    db.commit()
