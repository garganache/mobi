# TASK-049: Backend - Add GET /api/listings/:id Endpoint

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Completed  
**Priority:** High  
**Estimated:** 20 min

## Objective

Create a backend API endpoint to retrieve a single property listing by ID.

## Requirements

1. Add `GET /api/listings/{id}` endpoint in FastAPI
2. Query database for specific listing by ID
3. Return full listing object with all fields
4. Return 404 if listing not found
5. Return all data needed for detail view

## Acceptance Criteria

- [x] Endpoint returns single listing by ID
- [x] Returns 404 if ID doesn't exist
- [x] Response includes all listing fields
- [x] Fast response (<100ms)

## Technical Details

```python
# backend/app/routes/listings.py

from fastapi import HTTPException

@app.get("/api/listings/{listing_id}")
async def get_listing(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """Get a single listing by ID."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {
        "id": listing.id,
        "property_type": listing.property_type,
        "price": listing.price,
        "bedrooms": listing.bedrooms,
        "bathrooms": listing.bathrooms,
        "square_feet": listing.square_feet,
        "address": listing.address,
        "city": listing.city,
        "state": listing.state,
        "zip": listing.zip,
        "images": listing.images,
        "description": listing.description,
        "amenities_by_room": listing.amenities_by_room,
        "total_rooms": listing.total_rooms,
        "room_breakdown": listing.room_breakdown,
        "unified_description": listing.unified_description,
        "created_at": listing.created_at.isoformat(),
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
    }
```

## Files to Create/Modify

- `backend/app/routes/listings.py` (extend)

## Testing

Manual test:
```bash
# Existing listing
curl http://localhost:8000/api/listings/1

# Non-existent listing
curl http://localhost:8000/api/listings/99999
# Should return 404
```

Expected response:
```json
{
  "id": 1,
  "property_type": "apartment",
  "price": 250000,
  "bedrooms": 2,
  "bathrooms": 1,
  ...
}
```

- [x] Returns listing for valid ID
- [x] Returns 404 for invalid ID
- [x] Includes all database fields
- [x] Properly serializes complex fields (images, amenities)

## Dependencies

- TASK-048 (listings router setup)

## Notes

- Return ALL fields, even if null/empty
- Ensure proper JSON serialization of complex fields
- Consider adding `view_count` field for future analytics
- Images should be ready to display (data URLs or accessible paths)
