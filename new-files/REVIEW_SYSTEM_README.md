# Review and Feedback System Documentation

This document outlines the review and feedback system for the Accessibility Helper app.

## Overview

The review system allows disabled users to rate and provide feedback on helpers (drivers) after completing a request. This helps maintain service quality and allows users to make informed decisions when selecting helpers.

## Architecture

### Backend (Python/FastAPI)

**Location**: `/backend/routes/reviews.py`

#### Endpoints

1. **POST `/reviews/`**
   - Create a new review
   - Validates that:
     - Request exists and belongs to the user
     - Request is completed
     - Driver matches the request
   - Returns: Created review with driver name

2. **GET `/reviews/driver/{driver_id}`**
   - Get all reviews and stats for a specific driver
   - Returns: Average rating, total reviews, and recent reviews
   - Query param: `limit` (default 10) for number of recent reviews

3. **GET `/reviews/my-reviews`**
   - Get all reviews written by the current user
   - Returns: List of reviews with driver names

4. **PUT `/reviews/{review_id}`**
   - Update an existing review
   - Only the author can update
   - Can update rating and/or comment

5. **DELETE `/reviews/{review_id}`**
   - Delete a review
   - Only the author can delete

#### Data Models

```python
class ReviewCreate(BaseModel):
    rating: int  # 1-5
    comment: Optional[str]  # max 1000 chars
    driver_id: int
    request_id: int
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
    driver_name: string
    average_rating: float
    total_reviews: int
    recent_reviews: list[ReviewResponse]
```

### Frontend (SvelteKit)

#### Components

1. **ReviewForm.svelte**
   - Interactive 5-star rating system
   - Optional comment field (max 1000 chars)
   - Character counter
   - Success animation
   - Error handling
   
2. **DriverReviews.svelte**
   - Display driver stats (name, average rating, total reviews)
   - Rating distribution chart
   - List of recent reviews with comments
   - Relative date formatting ("2 days ago", etc.)
   
3. **HelperRating.svelte**
   - Compact rating display for request lists
   - Shows star rating and average
   - "New Helper" badge for helpers with no reviews
   - Two modes: compact and full

#### Pages

**complete-request/+page.svelte**
- Workflow for completing requests
- Shows request details
- "Mark as Completed" button
- Automatically shows review form after completion
- Optional skip button

## User Flow

### For Disabled Users

1. **After Request Completion**
   ```
   Request Details Page
   ↓
   Click "Mark as Completed"
   ↓
   Review Form Appears
   ↓
   Select Rating (1-5 stars)
   ↓
   (Optional) Add Comment
   ↓
   Submit Review
   ↓
   Success Message
   ↓
   Redirect to Dashboard
   ```

2. **Viewing Helper Ratings**
   - See average rating on request cards
   - Click to view full review history
   - See rating distribution and recent comments

### For Helpers

- View their own rating and reviews
- See aggregated stats
- Cannot modify or delete reviews about them

## Database Considerations

### Current Schema

The `reviews` table has:
- `rating` (smallint, 1-5)
- `comment` (text, optional)
- `driver` (foreign key to driver)
- `author` (foreign key to disabled)

### Recommended Improvements

1. **Link reviews to specific requests**
   ```sql
   ALTER TABLE reviews 
   ADD COLUMN request_id bigint,
   ADD COLUMN request_type text CHECK (request_type IN ('drive', 'shop'));
   ```
   This prevents duplicate reviews for the same request.

2. **Add helpful/not helpful votes**
   ```sql
   ALTER TABLE reviews
   ADD COLUMN helpful_count integer DEFAULT 0,
   ADD COLUMN not_helpful_count integer DEFAULT 0;
   ```

3. **Response from helpers**
   ```sql
   ALTER TABLE reviews
   ADD COLUMN helper_response text,
   ADD COLUMN helper_response_date timestamp with time zone;
   ```

## Features

### Implemented

✅ 1-5 star rating system  
✅ Optional text comments (max 1000 chars)  
✅ Average rating calculation  
✅ Rating distribution visualization  
✅ Recent reviews display  
✅ Review edit and delete (by author)  
✅ Driver stats aggregation  
✅ Relative date formatting  
✅ "New Helper" badge  
✅ Character counter  
✅ Success animations  
✅ Error handling  
✅ Mobile responsive design  

### Future Enhancements

🔲 Link reviews to specific requests (prevent duplicates)  
🔲 Helper response to reviews  
🔲 Helpful/not helpful voting  
🔲 Report inappropriate reviews  
🔲 Filter reviews (most recent, highest/lowest rated)  
🔲 Photo uploads with reviews  
🔲 Email notifications for new reviews  
🔲 Review moderation system  
🔲 Verified completion badge  
🔲 Review statistics for disabled users (how many they've left)  

## API Integration

### Authentication

In production, add authentication middleware:

```python
from fastapi import Header

async def get_current_user(
    authorization: str = Header(None)
) -> int:
    # Validate JWT token
    # Return user_id
    pass
```

Then use in endpoints:
```python
@router.post("/")
async def create_review(
    review: ReviewCreate,
    user_id: int = Depends(get_current_user)
):
    ...
```

### Frontend API Calls

Add auth headers:
```javascript
fetch('/api/reviews', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(reviewData)
})
```

## Usage Examples

### Creating a Review

```javascript
const review = {
  rating: 5,
  comment: "Excellent service! Very helpful and professional.",
  driver_id: 123,
  request_id: 456,
  request_type: "drive"
};

const response = await fetch('/api/reviews', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(review)
});
```

### Getting Driver Stats

```javascript
const driverId = 123;
const response = await fetch(`/api/reviews/driver/${driverId}?limit=5`);
const stats = await response.json();

console.log(stats.average_rating);  // 4.5
console.log(stats.total_reviews);   // 23
console.log(stats.recent_reviews);  // Array of 5 most recent
```

## Accessibility

The review system includes:
- Keyboard navigation for star ratings
- ARIA labels for screen readers
- High contrast colors
- Reduced motion support
- Clear focus indicators
- Semantic HTML

## Performance

- Reviews are paginated (default 10)
- Driver stats are cached on first load
- Lazy loading for review lists
- Optimistic UI updates

## Security

- Users can only review completed requests
- Users can only review their own requests
- SQL injection prevention via parameterized queries
- XSS prevention via input sanitization
- Rate limiting recommended for production

## Testing

Recommended test cases:
1. Create review for completed request
2. Attempt review on incomplete request (should fail)
3. Attempt review on someone else's request (should fail)
4. Update own review
5. Attempt to update someone else's review (should fail)
6. Delete own review
7. View driver with no reviews
8. View driver with multiple reviews
9. Calculate average rating correctly
10. Handle edge cases (empty comments, etc.)

## Environment Variables

Required in `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

## Deployment Notes

1. Set up CORS for production domains
2. Enable rate limiting
3. Add authentication middleware
4. Set up error monitoring (Sentry, etc.)
5. Configure database indexes:
   ```sql
   CREATE INDEX idx_reviews_driver ON reviews(driver);
   CREATE INDEX idx_reviews_author ON reviews(author);
   CREATE INDEX idx_reviews_created ON reviews(created_at DESC);
   ```

## Support

For questions or issues with the review system, please contact the development team.
