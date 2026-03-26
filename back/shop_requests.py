from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from gemini_service import get_ai_advice

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
    # Get the disabled person's information to fetch their disability
    disabled_person = db.query(models.Disabled).filter(models.Disabled.id == payload.disabled).first()
    if not disabled_person:
        raise HTTPException(status_code=404, detail="Disabled person not found")
    
    # Prepare the record data
    record_data = payload.model_dump()
    
    # Get AI advice based on disability and request description
    ai_advice = get_ai_advice(
        disability=disabled_person.disability,
        request_description=payload.description,
        request_type="shop"
    )
    record_data["ai_advice"] = ai_advice
    
    # Create and save the record
    record = models.ShopRequest(**record_data)
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
