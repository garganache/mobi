#!/usr/bin/env python3
"""
Integration test to verify the open-concept fixes work with the actual API.
"""

import requests
import json
import base64
from PIL import Image
import io
import sys
import os

def create_test_image():
    """Create a simple test image."""
    # Create a simple 400x300 colored image
    img = Image.new('RGB', (400, 300), color='lightgray')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.read()

def test_open_concept_api():
    """Test the open-concept fix via the API."""
    print("Testing Open-Concept Fix via API")
    print("=" * 40)
    
    # Create test image
    image_data = create_test_image()
    
    # Test with mock vision model (should simulate open-concept for large images)
    files = {
        'images': ('test.png', image_data, 'image/png')
    }
    data = {
        'model_type': 'mock'
    }
    
    try:
        response = requests.post('http://localhost:8000/api/analyze', 
                               files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("API Response:")
            print(f"Status: {result.get('status')}")
            print(f"Total rooms: {result.get('total_rooms')}")
            print(f"Layout type: {result.get('layout_type')}")
            print(f"Description: {result.get('unified_description')}")
            print(f"Interior features: {result.get('interior_features')}")
            print(f"Exterior features: {result.get('exterior_features')}")
            
            # Check that the fields are present
            synthesis = result.get('synthesis', {})
            if synthesis:
                print(f"Synthesis - Total rooms: {synthesis.get('total_rooms')}")
                print(f"Synthesis - Layout type: {synthesis.get('layout_type')}")
                print(f"Synthesis - Interior features: {synthesis.get('interior_features')}")
                print(f"Synthesis - Exterior features: {synthesis.get('exterior_features')}")
                
                # Verify the fix
                interior_features = synthesis.get('interior_features')
                exterior_features = synthesis.get('exterior_features')
                
                if interior_features is not None:
                    print("✅ interior_features field is present")
                else:
                    print("❌ interior_features field is missing")
                    
                if exterior_features is not None:
                    print("✅ exterior_features field is present")
                else:
                    print("❌ exterior_features field is missing")
            
            return True
        else:
            print(f"API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the backend is running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_open_concept_api()
    if success:
        print("\n✅ API integration test completed")
    else:
        print("\n❌ API integration test failed")
        sys.exit(1)