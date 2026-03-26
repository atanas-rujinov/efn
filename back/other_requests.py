from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import require_disabled 

router = APIRouter(prefix="/other-requests", tags=["Other Requests"])

@router.get("/", response_model=List[schemas.OtherRequestOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.OtherRequest).all()

@router.get("/{id}", response_model=schemas.OtherRequestOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.OtherRequest).filter(models.OtherRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    return record

@router.post("/", response_model=schemas.OtherRequestOut, status_code=201)
def create(
    payload: schemas.OtherRequestCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_disabled) 
):
    data = payload.model_dump()
    data["disabled"] = current_user.id 
    
    record = models.OtherRequest(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.patch("/{id}", response_model=schemas.OtherRequestOut)
def update(id: int, payload: schemas.OtherRequestUpdate, db: Session = Depends(get_db)):
    record = db.query(models.OtherRequest).filter(models.OtherRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
        
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{id}", status_code=204)
def delete(id: int, db: Session = Depends(get_db)):
    record = db.query(models.OtherRequest).filter(models.OtherRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    db.delete(record)
    db.commit()