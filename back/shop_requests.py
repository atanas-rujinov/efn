from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter(prefix="/shop-requests", tags=["Shop Requests"])


@router.get("/", response_model=List[schemas.ShopRequestOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.ShopRequest).all()


@router.get("/{id}", response_model=schemas.ShopRequestOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.ShopRequest).filter(models.ShopRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Shop request not found")
    return record


@router.post("/", response_model=schemas.ShopRequestOut, status_code=201)
def create(payload: schemas.ShopRequestCreate, db: Session = Depends(get_db)):
    record = models.ShopRequest(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{id}", response_model=schemas.ShopRequestOut)
def update(id: int, payload: schemas.ShopRequestUpdate, db: Session = Depends(get_db)):
    record = db.query(models.ShopRequest).filter(models.ShopRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Shop request not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    record = db.query(models.ShopRequest).filter(models.ShopRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Shop request not found")
    db.delete(record)
    db.commit()
