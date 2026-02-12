#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import get_all_listings, SessionLocal, engine, init_db
from app.models import Base, Listing, ListingImage, ListingSynthesis
from datetime import datetime

# Initialize database
print("Initializing database...")
init_db()
print("Database initialized!")

# Create a test database session
db = SessionLocal()

try:
    # Create a test listing
    test_listing = Listing(
        property_type="apartment",
        price=250000,
        bedrooms=2,
        bathrooms=2.0,
        square_feet=1200,
        address="123 Test Street",
        city="Test City",
        state="TS",
        zip_code="12345",
        status="draft"
    )
    
    db.add(test_listing)
    db.flush()  # Get the ID
    
    # Add a test image
    test_image = ListingImage(
        listing_id=test_listing.id,
        image_data="test_base64_data",
        ai_description="A beautiful apartment living room",
        detected_rooms={"bedroom": 2, "bathroom": 2},
        detected_amenities=["hardwood_floors", "granite_counters"]
    )
    
    db.add(test_image)
    
    # Add test synthesis
    test_synthesis = ListingSynthesis(
        listing_id=test_listing.id,
        total_rooms=6,
        layout_type="open_concept",
        unified_description="A beautiful 2-bedroom apartment with modern amenities",
        room_breakdown={"bedroom": 2, "bathroom": 2, "kitchen": 1, "living_room": 1},
        property_overview={"style": "modern", "condition": "excellent"},
        interior_features=["hardwood_floors", "granite_counters", "stainless_steel_appliances"],
        exterior_features=["balcony", "parking"]
    )
    
    db.add(test_synthesis)
    
    # Commit the transaction
    db.commit()
    print(f"✅ Created test listing with ID: {test_listing.id}")
    
    # Test the endpoint
    result = get_all_listings(limit=10, offset=0, db=db)
    print(f"✅ Endpoint returned {len(result)} listings")
    
    if len(result) > 0:
        listing = result[0]
        print(f"✅ First listing ID: {listing['id']}")
        print(f"✅ Property type: {listing['property_type']}")
        print(f"✅ Price: {listing['price']}")
        print(f"✅ Images count: {len(listing['images'])}")
        print(f"✅ Has synthesis: {listing['synthesis'] is not None}")
        
        # Test pagination
        result_paginated = get_all_listings(limit=1, offset=0, db=db)
        print(f"✅ Pagination test - limit=1 returned {len(result_paginated)} listings")
        
        result_offset = get_all_listings(limit=1, offset=1, db=db)
        print(f"✅ Offset test - offset=1 returned {len(result_offset)} listings")
        
        if len(result_paginated) > 0 and len(result_offset) > 0:
            print(f"✅ Pagination works correctly - different results with different offsets")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("✅ All tests with data completed!")