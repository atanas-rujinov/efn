"""
Integration example for the Review System
This file shows how to integrate the review endpoints into your main FastAPI app
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.reviews import router as reviews_router

app = FastAPI(title="Accessibility Helper API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the reviews router
app.include_router(reviews_router)

# Other routers would go here
# app.include_router(auth_router)
# app.include_router(drive_requests_router)
# app.include_router(shop_requests_router)

@app.get("/")
async def root():
    return {"message": "Accessibility Helper API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Example: Adding review notification after request completion
from fastapi import APIRouter, HTTPException
from supabase import Client

completion_router = APIRouter(prefix="/requests", tags=["requests"])

@completion_router.patch("/{request_type}/{request_id}/complete")
async def complete_request(
    request_type: str,
    request_id: int,
    user_id: int,  # From auth in production
    supabase: Client = None  # Dependency inject
):
    """
    Mark a request as completed.
    This triggers the review flow on the frontend.
    """
    if request_type not in ["drive", "shop"]:
        raise HTTPException(status_code=400, detail="Invalid request type")
    
    table_name = f"{request_type}_requests"
    
    # Verify ownership
    request = supabase.table(table_name).select("*").eq("id", request_id).execute()
    if not request.data or request.data[0]["disabled"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Update completion status
    result = supabase.table(table_name).update({
        "is_completed": True
    }).eq("id", request_id).execute()
    
    # Optional: Send notification to user to leave a review
    # send_review_reminder_email(user_id, request_id, request_type)
    
    return {"message": "Request completed", "data": result.data[0]}

app.include_router(completion_router)


# Example: Showing helper ratings in request list
@completion_router.get("/available")
async def get_available_requests(
    request_type: str,
    user_lat: float,
    user_lon: float,
    limit: int = 20,
    supabase: Client = None
):
    """
    Get available requests with helper ratings.
    This is used by helpers to see requests they can accept.
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        """Calculate distance between two points in km"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    table_name = f"{request_type}_requests"
    
    # Get uncompleted requests
    requests = supabase.table(table_name).select(
        "*, disabled!{request_type}_requests_disabled_fkey(name), driver!{request_type}_requests_driver_fkey(id, name)"
    ).eq("is_completed", False).execute()
    
    # Calculate distances and add driver ratings
    enriched_requests = []
    for req in requests.data:
        distance = haversine(user_lon, user_lat, req["start_lon"], req["start_lat"])
        
        # Get driver rating if assigned
        driver_rating = None
        if req["driver"]:
            reviews = supabase.table("reviews").select("rating").eq(
                "driver", req["driver"]["id"]
            ).execute()
            
            if reviews.data:
                avg_rating = sum(r["rating"] for r in reviews.data) / len(reviews.data)
                driver_rating = {
                    "average": round(avg_rating, 2),
                    "count": len(reviews.data)
                }
        
        enriched_requests.append({
            **req,
            "distance_km": round(distance, 2),
            "driver_rating": driver_rating
        })
    
    # Sort by distance
    enriched_requests.sort(key=lambda x: x["distance_km"])
    
    return {"requests": enriched_requests[:limit]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
