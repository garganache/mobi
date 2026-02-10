# Database Schema Documentation

This document describes the database schema for the Mobi real estate platform.

## Models

### 1. Listing Model
**Table:** `listings`

Represents a real estate property listing with basic property information.

**Fields:**
- `id` (Integer, Primary Key) - Unique identifier
- `property_type` (String, Required) - Type of property (apartment, house, condo, etc.)
- `price` (Integer) - Price in cents/dollars
- `bedrooms` (Integer) - Number of bedrooms
- `bathrooms` (Float) - Number of bathrooms
- `square_feet` (Integer) - Square footage
- `address` (String) - Street address
- `city` (String) - City name
- `state` (String) - State abbreviation
- `zip_code` (String) - ZIP code
- `status` (String, Default: "draft") - Listing status (draft, published, archived)
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

**Relationships:**
- One-to-many with `ListingImage` (images)
- One-to-one with `ListingSynthesis` (synthesis)

### 2. ListingImage Model
**Table:** `listing_images`

Represents an image associated with a listing, including AI analysis results.

**Fields:**
- `id` (Integer, Primary Key) - Unique identifier
- `listing_id` (Integer, Foreign Key) - Associated listing ID
- `image_data` (Text) - Base64 encoded image data (for MVP)
- `image_url` (String) - Optional URL if using external storage
- `ai_description` (Text) - AI-generated description of the image
- `detected_rooms` (JSON) - Room detection results (e.g., {"bedroom": 2, "kitchen": 1})
- `detected_amenities` (JSON) - Detected amenities (e.g., ["hardwood_floors", "granite"])
- `property_type` (String) - Detected property type
- `style` (String) - Detected architectural style
- `condition` (String) - Detected condition
- `order_index` (Integer, Default: 0) - Display order for images
- `created_at` (DateTime) - Creation timestamp

**Relationships:**
- Many-to-one with `Listing` (listing)

### 3. ListingSynthesis Model
**Table:** `listing_synthesis`

Represents the synthesized analysis of all images and data for a listing.

**Fields:**
- `id` (Integer, Primary Key) - Unique identifier
- `listing_id` (Integer, Foreign Key, Unique) - Associated listing ID
- `total_rooms` (Integer) - Total number of rooms detected
- `layout_type` (String) - Layout type (open_concept, traditional, etc.)
- `unified_description` (Text) - AI-generated unified description
- `room_breakdown` (JSON) - Detailed room breakdown
- `property_overview` (JSON) - Complete property overview object
- `interior_features` (JSON) - List of interior amenities/features
- `exterior_features` (JSON) - List of exterior amenities/features
- `created_at` (DateTime) - Creation timestamp

**Relationships:**
- One-to-one with `Listing` (listing)

## Usage

### Creating Tables
The tables are automatically created when the FastAPI application starts up:

```python
from app.main import init_db
init_db()
```

### Using the Models
```python
from app.models import Listing, ListingImage, ListingSynthesis
from app.main import get_db

# Get database session
db = next(get_db())

# Create a listing
listing = Listing(
    property_type="apartment",
    price=150000,
    bedrooms=2,
    bathrooms=1.5,
    square_feet=800,
    address="123 Main St",
    city="New York",
    state="NY",
    zip_code="10001"
)
db.add(listing)
db.commit()

# Add an image with AI analysis
image = ListingImage(
    listing_id=listing.id,
    image_data="base64_encoded_image_data",
    ai_description="A beautiful living room with hardwood floors",
    detected_rooms={"living_room": 1, "bedroom": 2},
    detected_amenities=["hardwood_floors", "fireplace"],
    property_type="apartment",
    style="modern",
    condition="excellent"
)
db.add(image)

# Add synthesis data
synthesis = ListingSynthesis(
    listing_id=listing.id,
    total_rooms=4,
    layout_type="open_concept",
    unified_description="A modern apartment with open concept design",
    room_breakdown={"bedroom": 2, "bathroom": 1, "kitchen": 1},
    property_overview={"type": "apartment", "style": "modern"},
    interior_features=["granite_counters", "hardwood_floors"],
    exterior_features=["balcony"]
)
db.add(synthesis)
db.commit()
```

## Migration from Old Schema

The new schema replaces the previous `Description` and `ImageAnalysis` models. The old models are retained for backward compatibility during the transition period, but new code should use the `Listing`, `ListingImage`, and `ListingSynthesis` models.

## Testing

Run the model tests:
```bash
cd backend
source .venv/bin/activate
DATABASE_URL="sqlite:///:memory:" python -m pytest app/tests/test_models.py -v
```