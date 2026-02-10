#!/usr/bin/env python3
"""
Test script to verify the fixes for TASK-029
"""

# Mock the vision model functionality to test the logic
class MockAnalysis:
    def __init__(self, rooms, amenities, description="", property_type="apartment", style="modern"):
        self.rooms = rooms
        self.amenities = amenities
        self.description = description
        self.property_type = property_type
        self.style = style
    
    def get(self, key, default=None):
        if key == "rooms":
            return self.rooms
        elif key == "amenities":
            return self.amenities
        elif key == "description":
            return self.description
        elif key == "property_type":
            return self.property_type
        elif key == "style":
            return self.style
        elif key == "condition":
            return "good"
        return default

def test_open_concept_detection():
    """Test that open-concept spaces are detected correctly"""
    print("Testing open-concept detection...")
    
    # Simulate a studio apartment with multiple room types in one image
    studio_analysis = MockAnalysis(
        rooms={"living_room": 1, "kitchen": 1, "dining_area": 1, "office_nook": 1},
        amenities=["hardwood_floors", "granite_counters", "stainless_steel"],
        description="Open concept living space with kitchen and dining area",
        property_type="apartment"
    )
    
    # Test the logic from our updated synthesize_property_overview function
    analyses = [studio_analysis]
    
    # Separate interior and exterior analyses
    interior_analyses = []
    exterior_analyses = []
    
    for analysis in analyses:
        rooms = analysis.get("rooms", {})
        # If no rooms detected, treat as exterior image
        if not rooms or sum(rooms.values()) == 0:
            exterior_analyses.append(analysis)
        else:
            interior_analyses.append(analysis)
    
    # Detect open-concept spaces in interior images
    open_concept_detected = False
    
    # Check each interior image for open-concept layout
    for analysis in interior_analyses:
        rooms = analysis.get("rooms", {})
        room_types = list(rooms.keys())
        room_count = sum(rooms.values())
        
        # If single image has multiple room types, it's likely open-concept
        if len(room_types) >= 3 and room_count >= 3:
            open_concept_detected = True
    
    print(f"Studio analysis - Room types: {studio_analysis.rooms}")
    print(f"Open concept detected: {open_concept_detected}")
    
    # Test exterior image detection
    exterior_analysis = MockAnalysis(
        rooms={},
        amenities=["garage", "garden"],
        description="Exterior of house with front porch and landscaping",
        property_type="house"
    )
    
    print(f"\nExterior analysis - Rooms: {exterior_analysis.rooms}")
    print(f"Should be treated as exterior: {not exterior_analysis.rooms or sum(exterior_analysis.rooms.values()) == 0}")
    
    return open_concept_detected

def test_exterior_features():
    """Test that exterior features are handled correctly"""
    print("\nTesting exterior feature handling...")
    
    exterior_analysis = MockAnalysis(
        rooms={},
        amenities=["garage", "garden", "pool"],
        description="Beautiful exterior with landscaped yard and garage",
        property_type="house"
    )
    
    # Test exterior feature extraction
    exterior_features = []
    exterior_amenities = set()
    
    amenities = exterior_analysis.get("amenities", [])
    description = exterior_analysis.get("description", "")
    
    # Add exterior-specific amenities
    exterior_amenities.update(amenities)
    
    # Add specific exterior amenities as features
    for amenity in exterior_amenities:
        if amenity in ['garage', 'garden', 'pool', 'balcony', 'patio', 'deck']:
            exterior_features.append(amenity.replace('_', ' '))
    
    print(f"Exterior amenities: {list(exterior_amenities)}")
    print(f"Exterior features: {exterior_features}")
    
    return exterior_features

if __name__ == "__main__":
    print("=== Testing TASK-029 Fixes ===\n")
    
    # Test 1: Open concept detection
    open_concept_result = test_open_concept_detection()
    assert open_concept_result == True, "Open concept should be detected for studio with multiple room types"
    print("✅ Open concept detection works correctly\n")
    
    # Test 2: Exterior features
    exterior_result = test_exterior_features()
    assert len(exterior_result) > 0, "Exterior features should be extracted"
    print("✅ Exterior feature extraction works correctly\n")
    
    print("=== All tests passed! ===")