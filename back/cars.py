from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("/", response_model=List[schemas.CarOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Car).all()


@router.get("/{id}", response_model=schemas.CarOut)
def get_one(id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post("/", response_model=schemas.CarOut, status_code=201)
def create(payload: schemas.CarCreate, db: Session = Depends(get_db)):
    car = models.Car(**payload.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


@router.patch("/{id}", response_model=schemas.CarOut)
def update(id: int, payload: schemas.CarUpdate, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(car, field, value)
    db.commit()
    db.refresh(car)
    return car


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db.delete(car)
    db.commit()
