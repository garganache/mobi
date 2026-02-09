#!/usr/bin/env python3
"""
Debug script to check what's happening with the vision model.
"""

import sys
import os
sys.path.insert(0, '/home/ubuntu/mobi/backend')

from app.vision_model import analyze_property_image, create_vision_model

# Test with invalid image data (like the test does)
result = analyze_property_image(b"base64_encoded_image_data", model_type="mock")
print("Mock vision model result:")
print(f"Property type: {result.get('property_type')}")
print(f"Rooms: {result.get('rooms')}")
print(f"Amenities: {result.get('amenities')}")
print(f"Full result keys: {list(result.keys())}")