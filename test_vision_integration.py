#!/usr/bin/env python3
"""
Test script for vision model integration.
"""

import base64
import json
import logging
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.vision_model import analyze_property_image, create_vision_model
from app.feature_extractor import extract_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_image():
    """Create a simple test image."""
    from PIL import Image
    import io
    
    # Create a simple colored image
    img = Image.new('RGB', (800, 600), color='blue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()


def test_mock_vision_model():
    """Test the mock vision model."""
    print("Testing Mock Vision Model...")
    
    try:
        # Create test image
        image_data = create_test_image()
        
        # Test with mock model
        result = analyze_property_image(image_data, model_type="mock")
        
        print("✓ Mock vision model test passed")
        print(f"  Property type: {result.get('property_type')}")
        print(f"  Style: {result.get('style')}")
        print(f"  Amenities: {result.get('amenities', [])}")
        print(f"  Description: {result.get('description', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Mock vision model test failed: {e}")
        return False


def test_feature_extractor():
    """Test the feature extractor."""
    print("\nTesting Feature Extractor...")
    
    try:
        test_description = "A modern apartment with granite countertops, stainless steel appliances, and hardwood floors. Features a dishwasher and fireplace."
        
        features = extract_features(test_description)
        
        print("✓ Feature extractor test passed")
        print(f"  Property type: {features.get('property_type')}")
        print(f"  Style: {features.get('style')}")
        print(f"  Amenities: {features.get('amenities', [])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Feature extractor test failed: {e}")
        return False


def test_image_preprocessing():
    """Test image preprocessing."""
    print("\nTesting Image Preprocessing...")
    
    try:
        from app.vision_model import preprocess_image
        import io
        from PIL import Image
        
        # Create a large test image
        img = Image.new('RGB', (2000, 1500), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        original_data = img_bytes.getvalue()
        
        # Preprocess
        processed_data = preprocess_image(original_data, max_size=1024)
        
        print("✓ Image preprocessing test passed")
        print(f"  Original size: {len(original_data)} bytes")
        print(f"  Processed size: {len(processed_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Image preprocessing test failed: {e}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\nTesting Error Handling...")
    
    try:
        # Test with invalid image data - this should work with the mock model
        result = analyze_property_image(b"invalid image data", model_type="mock")
        print("✓ Error handling test passed")
        print("  Mock model handled invalid data gracefully")
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running Vision Model Integration Tests...\n")
    
    tests = [
        test_mock_vision_model,
        test_feature_extractor,
        test_image_preprocessing,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())