#!/usr/bin/env python3
"""
Integration test for TASK-029 fixes using the actual backend API
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.vision_model import synthesize_property_overview

def test_studio_open_concept():
    """Test that a studio apartment is detected as open-concept"""
    print("Testing studio apartment open-concept detection...")
    
    # Simulate analysis results for a studio apartment with multiple room types
    analyses = [
        {
            "description": "Open concept living space with kitchen, dining area, and office nook",
            "property_type": "apartment",
            "rooms": {"living_room": 1, "kitchen": 1, "dining_area": 1, "office_nook": 1},
            "amenities": ["hardwood_floors", "granite_counters", "stainless_steel"],
            "style": "modern",
            "materials": ["hardwood_floors", "granite_counters"],
            "condition": "excellent"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Layout type: {result.get('layout_type')}")
    print(f"Total rooms: {result.get('total_rooms')}")
    print(f"Room breakdown: {result.get('room_breakdown')}")
    print(f"Unified description: {result.get('unified_description')}")
    
    # Assertions
    assert result.get('layout_type') == 'open_concept', "Should detect open-concept layout"
    assert result.get('total_rooms') == 4, "Should count all 4 room areas"
    assert 'open-concept' in result.get('unified_description', '').lower(), "Description should mention open-concept"
    
    print("✅ Studio apartment correctly detected as open-concept")
    return True

def test_exterior_image_handling():
    """Test that exterior images are handled correctly"""
    print("\nTesting exterior image handling...")
    
    # Simulate analysis results for exterior images
    analyses = [
        {
            "description": "Modern kitchen with granite countertops and stainless steel appliances",
            "property_type": "house",
            "rooms": {"kitchen": 1},
            "amenities": ["granite_counters", "stainless_steel"],
            "style": "modern",
            "materials": ["granite_counters"],
            "condition": "excellent"
        },
        {
            "description": "Exterior of house with front porch, garage, and landscaped yard",
            "property_type": "house", 
            "rooms": {},  # No rooms detected - this should be treated as exterior
            "amenities": ["garage", "garden", "porch"],
            "style": "modern",
            "materials": [],
            "condition": "excellent"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Total rooms: {result.get('total_rooms')}")
    print(f"Room breakdown: {result.get('room_breakdown')}")
    print(f"Exterior features: {result.get('exterior_features')}")
    print(f"Unified description: {result.get('unified_description')}")
    
    # Assertions
    assert result.get('total_rooms') == 1, "Should only count interior rooms"
    assert len(result.get('exterior_features', [])) > 0, "Should extract exterior features"
    assert 'exterior' in result.get('unified_description', '').lower(), "Should mention exterior features"
    
    print("✅ Exterior images correctly separated and features extracted")
    return True

def test_traditional_layout():
    """Test that traditional layouts are detected correctly"""
    print("\nTesting traditional layout detection...")
    
    # Simulate analysis results for traditional separate rooms
    analyses = [
        {
            "description": "Spacious living room with fireplace",
            "property_type": "house",
            "rooms": {"living_room": 1},
            "amenities": ["fireplace", "hardwood_floors"],
            "style": "traditional",
            "materials": ["hardwood_floors"],
            "condition": "good"
        },
        {
            "description": "Kitchen with updated appliances",
            "property_type": "house",
            "rooms": {"kitchen": 1},
            "amenities": ["granite_counters", "stainless_steel"],
            "style": "traditional",
            "materials": ["granite_counters"],
            "condition": "good"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Layout type: {result.get('layout_type')}")
    print(f"Total rooms: {result.get('total_rooms')}")
    print(f"Unified description: {result.get('unified_description')}")
    
    # Assertions
    assert result.get('layout_type') == 'traditional', "Should detect traditional layout"
    assert result.get('total_rooms') == 2, "Should count 2 separate rooms"
    
    print("✅ Traditional layout correctly detected")
    return True

def test_empty_analyses():
    """Test handling of empty analyses"""
    print("\nTesting empty analyses handling...")
    
    result = synthesize_property_overview([])
    
    print(f"Result keys: {list(result.keys())}")
    print(f"Layout type: {result.get('layout_type')}")
    print(f"Exterior features: {result.get('exterior_features')}")
    
    # Assertions
    assert result.get('layout_type') == 'unknown', "Should return unknown for empty analyses"
    assert result.get('total_rooms') == 0, "Should have 0 rooms for empty analyses"
    assert isinstance(result.get('exterior_features'), list), "Should return empty list for exterior features"
    
    print("✅ Empty analyses handled correctly")
    return True

if __name__ == "__main__":
    print("=== Testing TASK-029 Integration Tests ===\n")
    
    all_tests_passed = True
    
    try:
        test_studio_open_concept()
        test_exterior_image_handling()
        test_traditional_layout()
        test_empty_analyses()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        all_tests_passed = False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        all_tests_passed = False
    
    if all_tests_passed:
        print("\n🎉 All integration tests passed!")
        print("\nTASK-029 fixes are working correctly:")
        print("✅ Open-concept spaces detected (studio shows as open-concept, not 4 separate rooms)")
        print("✅ Exterior images separated from interior analysis")
        print("✅ Exterior features extracted and displayed separately")
        print("✅ Traditional layouts still detected correctly")
        print("✅ Empty analyses handled gracefully")
    else:
        print("\n❌ Some tests failed - please check the implementation")
        sys.exit(1)