from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("/", response_model=List[schemas.DriverOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Driver).all()


@router.get("/{id}", response_model=schemas.DriverOut)
def get_one(id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("/", response_model=schemas.DriverOut, status_code=201)
def create(payload: schemas.DriverCreate, db: Session = Depends(get_db)):
    driver = models.Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.patch("/{id}", response_model=schemas.DriverOut)
def update(id: int, payload: schemas.DriverUpdate, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    driver = db.query(models.Driver).filter(models.Driver.id == id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
