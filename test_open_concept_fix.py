#!/usr/bin/env python3
"""
Test script to verify the open-concept room counting fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.vision_model import synthesize_property_overview

def test_open_concept_single_image():
    """Test case 1: Studio apartment (1 image with living+kitchen+dining+office)"""
    print("Test 1: Open-concept single image")
    
    analyses = [
        {
            "description": "A modern open-concept space with living area, kitchen, dining area, and office space",
            "property_type": "apartment",
            "rooms": {"living_room": 1, "kitchen": 1, "dining_room": 1, "office": 1},
            "amenities": ["hardwood_floors", "granite_counters", "stainless_steel"],
            "style": "modern",
            "materials": ["hardwood_floors", "granite_counters"],
            "condition": "excellent"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Total rooms: {result['total_rooms']}")
    print(f"Layout type: {result['layout_type']}")
    print(f"Room breakdown: {result['room_breakdown']}")
    print(f"Description: {result['unified_description']}")
    print(f"Interior features: {result.get('interior_features', 'MISSING')}")
    print(f"Exterior features: {result.get('exterior_features', 'MISSING')}")
    print()
    
    # Assertions
    assert result['total_rooms'] == 1, f"Expected 1 room, got {result['total_rooms']}"
    assert result['layout_type'] == 'open_concept', f"Expected open_concept, got {result['layout_type']}"
    assert 'open_concept_space' in result['room_breakdown'], "Expected open_concept_space in room_breakdown"
    assert '1 open-concept space' in result['unified_description'], f"Expected '1 open-concept space' in description, got: {result['unified_description']}"
    assert result.get('interior_features') is not None, "interior_features should not be None"
    assert result.get('exterior_features') is not None, "exterior_features should not be None"
    
    print("✅ Test 1 passed!")
    print()

def test_open_concept_with_exterior():
    """Test case 2: Studio + exterior (2 images)"""
    print("Test 2: Open-concept with exterior")
    
    analyses = [
        {
            "description": "A modern open-concept space with living area, kitchen, dining area, and office space",
            "property_type": "apartment",
            "rooms": {"living_room": 1, "kitchen": 1, "dining_room": 1, "office": 1},
            "amenities": ["hardwood_floors", "granite_counters", "stainless_steel"],
            "style": "modern",
            "materials": ["hardwood_floors", "granite_counters"],
            "condition": "excellent"
        },
        {
            "description": "Exterior view showing front porch and landscaped garden",
            "property_type": "apartment",
            "rooms": {},
            "amenities": ["front_porch", "landscaping"],
            "style": "modern",
            "materials": [],
            "condition": "excellent"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Total rooms: {result['total_rooms']}")
    print(f"Layout type: {result['layout_type']}")
    print(f"Room breakdown: {result['room_breakdown']}")
    print(f"Description: {result['unified_description']}")
    print(f"Interior features: {result.get('interior_features', 'MISSING')}")
    print(f"Exterior features: {result.get('exterior_features', 'MISSING')}")
    print()
    
    # Assertions
    assert result['total_rooms'] == 1, f"Expected 1 room, got {result['total_rooms']}"
    assert result['layout_type'] == 'open_concept', f"Expected open_concept, got {result['layout_type']}"
    assert len(result.get('exterior_features', [])) > 0, "Expected exterior features"
    assert result.get('interior_features') is not None, "interior_features should not be None"
    assert result.get('exterior_features') is not None, "exterior_features should not be None"
    
    print("✅ Test 2 passed!")
    print()

def test_traditional_multiple_rooms():
    """Test case 3: Multiple traditional rooms (3 separate room images)"""
    print("Test 3: Traditional multiple rooms")
    
    analyses = [
        {
            "description": "A spacious living room with hardwood floors",
            "property_type": "house",
            "rooms": {"living_room": 1},
            "amenities": ["hardwood_floors"],
            "style": "traditional",
            "materials": ["hardwood_floors"],
            "condition": "good"
        },
        {
            "description": "A modern kitchen with granite countertops",
            "property_type": "house",
            "rooms": {"kitchen": 1},
            "amenities": ["granite_counters", "stainless_steel"],
            "style": "traditional",
            "materials": ["granite_counters", "stainless_steel"],
            "condition": "excellent"
        },
        {
            "description": "A cozy bedroom with large windows",
            "property_type": "house",
            "rooms": {"bedroom": 1},
            "amenities": ["large_windows"],
            "style": "traditional",
            "materials": [],
            "condition": "good"
        }
    ]
    
    result = synthesize_property_overview(analyses)
    
    print(f"Total rooms: {result['total_rooms']}")
    print(f"Layout type: {result['layout_type']}")
    print(f"Room breakdown: {result['room_breakdown']}")
    print(f"Description: {result['unified_description']}")
    print(f"Interior features: {result.get('interior_features', 'MISSING')}")
    print(f"Exterior features: {result.get('exterior_features', 'MISSING')}")
    print()
    
    # Assertions
    assert result['total_rooms'] == 3, f"Expected 3 rooms, got {result['total_rooms']}"
    assert result['layout_type'] == 'traditional', f"Expected traditional, got {result['layout_type']}"
    assert result.get('interior_features') is not None, "interior_features should not be None"
    assert result.get('exterior_features') is not None, "exterior_features should not be None"
    
    print("✅ Test 3 passed!")
    print()

if __name__ == "__main__":
    print("Testing Open-Concept Room Counting Fixes")
    print("=" * 50)
    print()
    
    try:
        test_open_concept_single_image()
        test_open_concept_with_exterior()
        test_traditional_multiple_rooms()
        
        print("🎉 All tests passed! The fixes are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)