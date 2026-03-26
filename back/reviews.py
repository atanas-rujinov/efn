from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=List[schemas.ReviewOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Review).all()


@router.get("/{id}", response_model=schemas.ReviewOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    return record


@router.post("/", response_model=schemas.ReviewOut, status_code=201)
def create(payload: schemas.ReviewCreate, db: Session = Depends(get_db)):
    record = models.Review(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{id}", response_model=schemas.ReviewOut)
def update(id: int, payload: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(record)
    db.commit()
