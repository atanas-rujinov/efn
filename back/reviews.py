from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from auth import require_disabled
import models, schemas

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=List[schemas.ReviewOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Review).all()


@router.get("/by-driver/{driver_id}", response_model=List[schemas.ReviewOut])
def get_by_driver(driver_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific driver/helper"""
    reviews = db.query(models.Review).filter(models.Review.driver == driver_id).all()
    return reviews


@router.get("/{id}", response_model=schemas.ReviewOut)
def get_one(id: int, db: Session = Depends(get_db)):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    return record


@router.post("/", response_model=schemas.ReviewOut, status_code=201)
def create(
    payload: schemas.ReviewCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_disabled)
):
    # Ensure the author is the current logged-in disabled person
    if payload.author != current_user.id:
        raise HTTPException(status_code=403, detail="You can only review for yourself")
    
    # Check if this disabled person has already reviewed this driver
    existing_review = db.query(models.Review).filter(
        models.Review.driver == payload.driver,
        models.Review.author == payload.author
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="You have already reviewed this driver"
        )
    
    record = models.Review(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{id}", response_model=schemas.ReviewOut)
def update(
    id: int, 
    payload: schemas.ReviewUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_disabled)
):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Ensure only the author can update their own review
    if record.author != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own review")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}", status_code=204)
def delete(
    id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(require_disabled)
):
    record = db.query(models.Review).filter(models.Review.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Ensure only the author can delete their own review
    if record.author != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own review")
    
    db.delete(record)
    db.commit()
