from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from supabase import Client
import os
from datetime import datetime

router = APIRouter(prefix="/reviews", tags=["reviews"])

# Pydantic models for request/response
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)
    driver_id: int
    request_id: int  # Either drive_request or shop_request ID
    request_type: str  # "drive" or "shop"

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    driver_id: int
    author_id: int
    created_at: str
    driver_name: str

class DriverStats(BaseModel):
    driver_id: int
    driver_name: str
    average_rating: float
    total_reviews: int
    recent_reviews: list[ReviewResponse]

# Dependency to get Supabase client
def get_supabase() -> Client:
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    disabled_id: int,  # This should come from auth token in production
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new review for a driver after completing a request.
    Only the disabled person who made the request can leave a review.
    """
    try:
        # Verify the request exists and belongs to this disabled user
        table_name = f"{review.request_type}_requests"
        request_data = supabase.table(table_name).select("*").eq("id", review.request_id).execute()
        
        if not request_data.data:
            raise HTTPException(status_code=404, detail="Request not found")
        
        request = request_data.data[0]
        
        # Verify ownership and completion
        if request["disabled"] != disabled_id:
            raise HTTPException(status_code=403, detail="You can only review your own requests")
        
        if not request["is_completed"]:
            raise HTTPException(status_code=400, detail="Cannot review incomplete request")
        
        if request["driver"] != review.driver_id:
            raise HTTPException(status_code=400, detail="Driver ID mismatch")
        
        # Check if review already exists for this request
        existing_review = supabase.table("reviews").select("*").eq(
            "driver", review.driver_id
        ).eq("author", disabled_id).execute()
        
        # In a more robust system, you'd link reviews to specific requests
        # For now, we'll allow multiple reviews per driver from the same user
        
        # Create the review
        review_data = {
            "rating": review.rating,
            "comment": review.comment,
            "driver": review.driver_id,
            "author": disabled_id
        }
        
        result = supabase.table("reviews").insert(review_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create review")
        
        # Get driver name for response
        driver = supabase.table("driver").select("name").eq("id", review.driver_id).execute()
        driver_name = driver.data[0]["name"] if driver.data else "Unknown"
        
        review_obj = result.data[0]
        return ReviewResponse(
            id=review_obj["id"],
            rating=review_obj["rating"],
            comment=review_obj["comment"],
            driver_id=review_obj["driver"],
            author_id=review_obj["author"],
            created_at=review_obj["created_at"],
            driver_name=driver_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating review: {str(e)}")

@router.get("/driver/{driver_id}", response_model=DriverStats)
async def get_driver_reviews(
    driver_id: int,
    limit: int = 10,
    supabase: Client = Depends(get_supabase)
):
    """
    Get all reviews for a specific driver, including average rating and recent reviews.
    """
    try:
        # Get all reviews for this driver
        reviews = supabase.table("reviews").select(
            "*, disabled!reviews_author_fkey(name)"
        ).eq("driver", driver_id).order("created_at", desc=True).execute()
        
        if not reviews.data:
            # Driver exists but has no reviews yet
            driver = supabase.table("driver").select("name").eq("id", driver_id).execute()
            if not driver.data:
                raise HTTPException(status_code=404, detail="Driver not found")
            
            return DriverStats(
                driver_id=driver_id,
                driver_name=driver.data[0]["name"],
                average_rating=0.0,
                total_reviews=0,
                recent_reviews=[]
            )
        
        # Calculate average rating
        total_rating = sum(r["rating"] for r in reviews.data)
        average_rating = total_rating / len(reviews.data)
        
        # Get driver name
        driver = supabase.table("driver").select("name").eq("id", driver_id).execute()
        driver_name = driver.data[0]["name"] if driver.data else "Unknown"
        
        # Format recent reviews
        recent_reviews = []
        for review in reviews.data[:limit]:
            recent_reviews.append(ReviewResponse(
                id=review["id"],
                rating=review["rating"],
                comment=review["comment"],
                driver_id=review["driver"],
                author_id=review["author"],
                created_at=review["created_at"],
                driver_name=driver_name
            ))
        
        return DriverStats(
            driver_id=driver_id,
            driver_name=driver_name,
            average_rating=round(average_rating, 2),
            total_reviews=len(reviews.data),
            recent_reviews=recent_reviews
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")

@router.get("/my-reviews")
async def get_my_reviews(
    disabled_id: int,  # From auth token in production
    supabase: Client = Depends(get_supabase)
):
    """
    Get all reviews written by the current disabled user.
    """
    try:
        reviews = supabase.table("reviews").select(
            "*, driver!reviews_driver_fkey(name)"
        ).eq("author", disabled_id).order("created_at", desc=True).execute()
        
        formatted_reviews = []
        for review in reviews.data:
            formatted_reviews.append({
                "id": review["id"],
                "rating": review["rating"],
                "comment": review["comment"],
                "driver_name": review["driver"]["name"],
                "created_at": review["created_at"]
            })
        
        return {"reviews": formatted_reviews}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")

@router.put("/{review_id}")
async def update_review(
    review_id: int,
    rating: Optional[int] = Field(None, ge=1, le=5),
    comment: Optional[str] = Field(None, max_length=1000),
    disabled_id: int = None,  # From auth token in production
    supabase: Client = Depends(get_supabase)
):
    """
    Update an existing review. Only the author can update their review.
    """
    try:
        # Verify ownership
        review = supabase.table("reviews").select("*").eq("id", review_id).execute()
        
        if not review.data:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.data[0]["author"] != disabled_id:
            raise HTTPException(status_code=403, detail="You can only update your own reviews")
        
        # Build update data
        update_data = {}
        if rating is not None:
            update_data["rating"] = rating
        if comment is not None:
            update_data["comment"] = comment
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Update the review
        result = supabase.table("reviews").update(update_data).eq("id", review_id).execute()
        
        return {"message": "Review updated successfully", "review": result.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    disabled_id: int,  # From auth token in production
    supabase: Client = Depends(get_supabase)
):
    """
    Delete a review. Only the author can delete their review.
    """
    try:
        # Verify ownership
        review = supabase.table("reviews").select("*").eq("id", review_id).execute()
        
        if not review.data:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.data[0]["author"] != disabled_id:
            raise HTTPException(status_code=403, detail="You can only delete your own reviews")
        
        # Delete the review
        supabase.table("reviews").delete().eq("id", review_id).execute()
        
        return {"message": "Review deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting review: {str(e)}")
