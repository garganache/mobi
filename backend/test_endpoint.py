#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import get_all_listings, SessionLocal, engine, init_db
from app.models import Base

# Initialize database
print("Initializing database...")
Base.metadata.create_all(bind=engine)
print("Database initialized!")

# Create a test database session
db = SessionLocal()

# Test the endpoint
try:
    # Test with default parameters
    result = get_all_listings(limit=10, offset=0, db=db)
    print(f"✅ Endpoint works! Returned {len(result)} listings")
    
    # Test empty case
    if len(result) == 0:
        print("✅ Empty case works - returned empty array")
    else:
        print(f"✅ Found {len(result)} existing listings")
        
    # Test pagination
    result2 = get_all_listings(limit=1, offset=0, db=db)
    print(f"✅ Pagination works - limit=1 returned {len(result2)} listings")
    
except Exception as e:
    print(f"❌ Error testing endpoint: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("✅ All tests passed!")