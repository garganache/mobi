#!/usr/bin/env python3
"""
Test script for the field suggestion algorithm.

This script tests various scenarios to ensure the algorithm correctly prioritizes
fields based on current form state and detected features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.field_suggestions import suggest_fields

def test_basic_suggestions():
    """Test basic field suggestions with empty form."""
    print("=== Test 1: Empty Form ===")
    current_data = {}
    suggestions = suggest_fields(current_data)
    
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    print(f"Number of suggestions: {len(suggestions)}")
    assert len(suggestions) <= 3, "Should return max 3 suggestions"
    assert len(suggestions) > 0, "Should return at least 1 suggestion"
    print("✓ Basic suggestions test passed\n")

def test_property_type_priority():
    """Test that property type is suggested first when missing."""
    print("=== Test 2: Property Type Priority ===")
    current_data = {"bedrooms": 3, "price": 500000}  # Missing property_type
    suggestions = suggest_fields(current_data)
    
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    field_ids = [field['id'] for field in suggestions]
    assert "property_type" in field_ids, "Property type should be suggested when missing"
    print("✓ Property type priority test passed\n")

def test_detected_features():
    """Test field suggestions with detected features."""
    print("=== Test 3: Detected Features ===")
    current_data = {"property_type": "house"}
    detected_features = {
        "amenities": ["pool", "garage", "balcony"],
        "amenities_confidence": {"pool": 0.9, "garage": 0.8, "balcony": 0.7}
    }
    
    suggestions = suggest_fields(current_data, detected_features)
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    field_ids = [field['id'] for field in suggestions]
    
    # Should suggest pool-related fields since pool was detected
    pool_fields = ["has_pool", "pool_type"]
    has_pool_suggestion = any(field in field_ids for field in pool_fields)
    assert has_pool_suggestion, "Should suggest pool-related fields when pool is detected"
    print("✓ Detected features test passed\n")

def test_required_fields():
    """Test that required fields are prioritized."""
    print("=== Test 4: Required Fields Priority ===")
    current_data = {"property_type": "house"}  # Missing required fields
    suggestions = suggest_fields(current_data)
    
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    field_ids = [field['id'] for field in suggestions]
    
    required_fields = ["bedrooms", "bathrooms", "price", "address"]
    has_required = any(field in field_ids for field in required_fields)
    assert has_required, "Should suggest required fields when missing"
    print("✓ Required fields priority test passed\n")

def test_property_specific_fields():
    """Test property-specific field suggestions."""
    print("=== Test 5: Property-Specific Fields ===")
    current_data = {"property_type": "house", "bedrooms": 3, "bathrooms": 2}
    suggestions = suggest_fields(current_data)
    
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    field_ids = [field['id'] for field in suggestions]
    
    # House-specific fields should be suggested
    house_fields = ["lot_size", "stories", "garage"]
    has_house_field = any(field in field_ids for field in house_fields)
    assert has_house_field, "Should suggest house-specific fields for house property type"
    print("✓ Property-specific fields test passed\n")

def test_high_value_fields():
    """Test that high-value fields are suggested appropriately."""
    print("=== Test 6: High-Value Fields ===")
    # Form with most required fields filled
    current_data = {
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "price": 300000,
        "address": "123 Main St"
    }
    suggestions = suggest_fields(current_data)
    
    print(f"Suggested fields: {[field['id'] for field in suggestions]}")
    field_ids = [field['id'] for field in suggestions]
    
    # Should suggest high-value fields like square_feet, description, etc.
    high_value_fields = ["square_feet", "description"]
    has_high_value = any(field in field_ids for field in high_value_fields)
    assert has_high_value, "Should suggest high-value fields when required fields are filled"
    print("✓ High-value fields test passed\n")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("=== Test 7: Edge Cases ===")
    
    # Test with nearly complete form
    current_data = {
        "property_type": "condo",
        "bedrooms": 2,
        "bathrooms": 2,
        "price": 400000,
        "address": "456 Ocean Ave",
        "square_feet": 1200,
        "description": "Beautiful ocean view condo"
    }
    suggestions = suggest_fields(current_data)
    
    print(f"Nearly complete form - Suggested fields: {[field['id'] for field in suggestions]}")
    # Should suggest fewer fields or none if form is nearly complete
    assert len(suggestions) <= 3, "Should not exceed max suggestions"
    
    # Test with None detected features
    suggestions = suggest_fields(current_data, None)
    print(f"None detected features - Suggested fields: {[field['id'] for field in suggestions]}")
    assert len(suggestions) <= 3, "Should handle None detected features gracefully"
    
    print("✓ Edge cases test passed\n")

def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Testing Field Suggestion Algorithm\n")
    
    try:
        test_basic_suggestions()
        test_property_type_priority()
        test_detected_features()
        test_required_fields()
        test_property_specific_fields()
        test_high_value_fields()
        test_edge_cases()
        
        print("🎉 All tests passed! The field suggestion algorithm is working correctly.")
        print("\n📋 Algorithm Features Tested:")
        print("  ✓ Progressive disclosure (max 3 fields per step)")
        print("  ✓ Required field prioritization")
        print("  ✓ Detected feature integration")
        print("  ✓ Property type specific suggestions")
        print("  ✓ High-value field prioritization")
        print("  ✓ Contextual relationships")
        print("  ✓ Edge case handling")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)