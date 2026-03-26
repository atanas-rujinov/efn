from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from auth import require_disabled
import models, schemas
from disability_grouping import get_disability_to_group_map, compute_group_ratings

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=List[schemas.ReviewOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(models.Review).all()


@router.get("/by-driver/{driver_id}", response_model=List[schemas.ReviewOut])
def get_by_driver(driver_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific driver/helper"""
    reviews = db.query(models.Review).filter(models.Review.driver == driver_id).all()
    return reviews


@router.get("/driver/{driver_id}", response_model=schemas.DriverStatsOut)
def get_driver_stats(
    driver_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Aggregated stats + recent reviews for a driver.
    This powers the DriverReviews / HelperRating UI snippets.
    """
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    q = (
        db.query(models.Review, models.Disabled.disability)
        .join(models.Disabled, models.Disabled.id == models.Review.author)
        .filter(models.Review.driver == driver_id)
        .order_by(models.Review.created_at.desc())
    )
    all_rows = q.all()
    all_reviews = [r for (r, _) in all_rows]

    total = len(all_reviews)
    avg = (sum(r.rating for r in all_reviews) / total) if total else 0.0

    recent = all_reviews[: max(0, limit)]
    recent_out = [
        schemas.ReviewWithDriverName(
            id=r.id,
            created_at=r.created_at,
            rating=r.rating,
            comment=r.comment,
            driver=r.driver,
            author=r.author,
            driver_name=driver.name,
        )
        for r in recent
    ]

    disability_to_group = get_disability_to_group_map(db)
    group_ratings = compute_group_ratings(all_rows, disability_to_group)

    return schemas.DriverStatsOut(
        driver_id=int(driver.id),
        driver_name=driver.name,
        average_rating=round(float(avg), 2),
        total_reviews=total,
        recent_reviews=recent_out,
        group_ratings=group_ratings,
    )


@router.get("/my-reviews", response_model=List[schemas.ReviewWithDriverName])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(require_disabled),
):
    """
    Reviews written by the current disabled user, including driver name.
    """
    rows = (
        db.query(models.Review, models.Driver.name)
        .join(models.Driver, models.Driver.id == models.Review.driver)
        .filter(models.Review.author == current_user.id)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return [
        schemas.ReviewWithDriverName(
            id=review.id,
            created_at=review.created_at,
            rating=review.rating,
            comment=review.comment,
            driver=review.driver,
            author=review.author,
            driver_name=driver_name,
        )
        for (review, driver_name) in rows
    ]


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

    # A review is only allowed if this disabled user has completed at least one ride
    # with this helper (not per-ride; still one review per disabled-helper pair).
    has_completed_ride = (
        db.query(models.DriveRequest)
        .filter(
            models.DriveRequest.disabled == current_user.id,
            models.DriveRequest.driver == payload.driver,
            models.DriveRequest.is_completed.is_(True),
        )
        .first()
    )
    if not has_completed_ride:
        raise HTTPException(
            status_code=403,
            detail="You can only review a helper after completing a ride with them",
        )

    # Single review per disabled-helper connection: create first, then update.
    existing_review = db.query(models.Review).filter(
        models.Review.driver == payload.driver,
        models.Review.author == payload.author
    ).first()

    if existing_review:
        existing_review.rating = payload.rating
        existing_review.comment = payload.comment
        db.commit()
        db.refresh(existing_review)
        return existing_review

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

    updates = payload.model_dump(exclude_unset=True)
    if "rating" in updates:
        record.rating = updates["rating"]
    if "comment" in updates:
        record.comment = updates["comment"]

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
