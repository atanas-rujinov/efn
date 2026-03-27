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
    # 1. Fetch real Drive Requests
    drive_records = db.query(models.DriveRequest).all()
    for r in drive_records:
        # Tag the real drive requests
        r.request_type = "drive"
    
    # 2. Fetch Other Requests
    other_records = db.query(models.OtherRequest).all()
    
    combined_others = []
    for r in other_records:
        # Convert to dict to inject "virtual" fields
        obj_dict = {column.name: getattr(r, column.name) for column in r.__table__.columns}
        
        # THE FIX: Tag as "other" so frontend knows to use otherRequestsApi
        obj_dict["request_type"] = "other"
        
        # Required dummy values for the DriveRequestOut schema
        obj_dict["start_address"] = "N/A"
        obj_dict["start_lat"] = 0.0
        obj_dict["start_lon"] = 0.0
        
        # Ensure the nested relationships match what the frontend expects
        # (Assuming your relationship names are disabled_rel and driver_rel)
        obj_dict["disabled_rel"] = r.disabled_rel 
        obj_dict["driver_rel"] = r.driver_rel

        combined_others.append(obj_dict)

    return list(drive_records) + combined_others

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


@router.patch("/{id}/reject-driver", response_model=schemas.DriveRequestOut)
def reject_driver(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_disabled),
):
    record = db.query(models.DriveRequest).filter(models.DriveRequest.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Drive request not found")
    if record.disabled != current_user.id:
        raise HTTPException(status_code=403, detail="You can only reject drivers on your own requests")
    if not record.is_accepted or record.driver is None:
        raise HTTPException(status_code=400, detail="No driver is currently assigned to this request")

    record.driver = None
    record.is_accepted = None
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