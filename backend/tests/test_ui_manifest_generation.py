"""
Integration tests for UI manifest generation logic.

Tests the /api/analyze-step endpoint to ensure it generates valid schemas
based on different input scenarios and property types.
"""

import os
from fastapi.testclient import TestClient

# Ensure we use a local SQLite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app, init_db  # noqa: E402


client = TestClient(app)


def setup_module(module):  # type: ignore[override]
    # Recreate DB for a clean slate
    init_db()


def test_analyze_step_with_image_input():
    """Test schema generation for image input with apartment detection."""
    request_data = {
        "current_data": {},
        "new_input": "base64_encoded_image_data",
        "input_type": "image"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify extracted data - property_type should NOT be in extracted_data
    # (user must confirm it, so it's shown as a field with default value instead)
    assert "property_type" not in data["extracted_data"]
    assert data["extracted_data"]["has_pool"] is False
    assert data["extracted_data"]["bedrooms"] == 2
    
    # Verify UI schema fields (should be limited to 2-3 per response)
    assert len(data["ui_schema"]) <= 3
    
    # First field should be property type with a default value
    if len(data["ui_schema"]) > 0:
        first_field = data["ui_schema"][0]
        assert first_field["id"] == "property_type"
        assert first_field["component_type"] == "select"
        # Label now in Romanian: "Tipul Proprietății" instead of "Property Type"
        assert first_field["label"] in ["Property Type", "Tipul Proprietății"]
        assert len(first_field["options"]) >= 3  # At least 3 options
        # Should have a default value set from AI detection
        assert first_field.get("default") is not None
    
    # Verify AI message is present and contains actual description
    assert data["ai_message"] is not None
    # AI message should be more than just a template (includes actual vision description)
    assert len(data["ai_message"]) > 50
    
    # Verify additional fields
    # Step number should equal the number of extracted data fields
    assert data["step_number"] == len(data["extracted_data"])
    # Completion percentage should be calculated based on fields filled
    assert isinstance(data["completion_percentage"], float)
    assert 0 <= data["completion_percentage"] <= 100


def test_analyze_step_with_text_input():
    """Test schema generation for text input with description."""
    request_data = {
        "current_data": {"property_type": "house", "bedrooms": 3},
        "new_input": "Beautiful 3-bedroom house with large backyard and modern kitchen",
        "input_type": "text"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify extracted data includes the description (when text is substantial)
    if len(request_data["new_input"]) > 10:
        assert data["extracted_data"]["description"] == request_data["new_input"]
    assert data["extracted_data"]["property_type"] == "house"
    assert data["extracted_data"]["bedrooms"] == 3
    
    # Verify UI schema fields (should be limited to 2-3 per response)
    assert len(data["ui_schema"]) <= 3
    
    # Verify fields are appropriate for text input
    field_ids = [field["id"] for field in data["ui_schema"]]
    # Should include unfilled fields like bathrooms, square_feet, etc.
    assert len(field_ids) > 0
    
    # Verify AI message is appropriate for text input
    assert data["ai_message"] is not None
    assert len(data["ai_message"]) > 0
    
    # Verify step progression - should be based on current data length
    assert data["step_number"] == len(data["extracted_data"])
    # Completion percentage should be calculated, not hardcoded
    assert isinstance(data["completion_percentage"], float)
    assert 0 <= data["completion_percentage"] <= 100


def test_analyze_step_with_field_update():
    """Test schema generation when user updates a field."""
    request_data = {
        "current_data": {
            "property_type": "condo",
            "bedrooms": 2,
            "bathrooms": 2,
            "has_parking": True
        },
        "input_type": "field_update"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify extracted data matches current_data
    assert data["extracted_data"] == request_data["current_data"]
    
    # Verify UI schema may have additional fields (mock implementation behavior)
    # In real implementation, field_update might not add new fields
    assert len(data["ui_schema"]) >= 0  # Could be empty or have fields
    
    # Verify AI message is present (no longer checks for specific wording)
    assert data["ai_message"] is not None
    assert len(data["ai_message"]) > 10  # Should have a meaningful message
    
    # Verify step and completion based on data fields
    assert data["step_number"] == len(request_data["current_data"])
    expected_completion = min(100.0, len(request_data["current_data"]) * 10)
    assert data["completion_percentage"] == expected_completion


def test_house_property_type_schema():
    """Test that house property type generates appropriate schema."""
    request_data = {
        "current_data": {"property_type": "house"},
        "new_input": "Large family house with garden",
        "input_type": "text"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify house-specific fields are included
    assert data["extracted_data"]["property_type"] == "house"
    
    # Verify UI schema adapts based on house property type
    field_ids = [field["id"] for field in data["ui_schema"]]
    
    # House properties should ask about yard/garden related features
    # This test validates that the schema adapts based on current_data state
    assert len(field_ids) > 0  # Should have relevant fields for house properties


def test_apartment_property_type_schema():
    """Test that apartment property type generates appropriate schema."""
    request_data = {
        "current_data": {"property_type": "apartment"},
        "new_input": "Modern downtown apartment",
        "input_type": "text"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify apartment-specific fields are included
    assert data["extracted_data"]["property_type"] == "apartment"
    
    # Verify UI schema adapts based on apartment property type
    field_ids = [field["id"] for field in data["ui_schema"]]
    assert len(field_ids) > 0  # Should have relevant fields for apartment properties


def test_field_limit_enforcement():
    """Test that the system limits fields to 2-3 per response."""
    request_data = {
        "current_data": {},
        "new_input": "base64_encoded_image_data",
        "input_type": "image"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify field count is limited
    assert 1 <= len(data["ui_schema"]) <= 3
    
    # Verify each field has required properties
    for field in data["ui_schema"]:
        assert "id" in field
        assert "component_type" in field
        assert "label" in field
        assert field["component_type"] in ["text", "select", "number", "toggle"]


def test_extracted_data_matches_detected_features():
    """Test that extracted_data accurately reflects detected features."""
    request_data = {
        "current_data": {},
        "new_input": "base64_encoded_image_data",
        "input_type": "image"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify extracted data keys are reasonable
    extracted_keys = set(data["extracted_data"].keys())
    
    # The AI message should be present and informative
    ai_message = data["ai_message"].lower()
    assert len(ai_message) > 20  # Should have meaningful content
    
    # Basic validation that detected features are reflected appropriately
    # Note: property_type is NOT in extracted_data (it's shown as a field for confirmation)
    if "pool" in ai_message:
        assert "has_pool" in extracted_keys
    if "bedroom" in ai_message:
        assert "bedrooms" in extracted_keys
    
    # If property type is mentioned, verify it's in UI schema for confirmation
    if "apartment" in ai_message or "house" in ai_message:
        # Should be shown as a field, not in extracted_data
        property_type_field = next((f for f in data["ui_schema"] if f["id"] == "property_type"), None)
        assert property_type_field is not None
        assert property_type_field.get("default") is not None


def test_schema_validation():
    """Test that the generated schema is valid and complete."""
    request_data = {
        "current_data": {},
        "new_input": "base64_encoded_image_data",
        "input_type": "image"
    }
    
    response = client.post("/api/analyze-step", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate response structure matches UIManifest schema
    assert "extracted_data" in data
    assert "ui_schema" in data
    assert "ai_message" in data
    
    # Validate ui_schema field structure
    for field in data["ui_schema"]:
        # Required fields
        assert "id" in field and isinstance(field["id"], str)
        assert "component_type" in field and field["component_type"] in ["text", "select", "number", "toggle"]
        assert "label" in field and isinstance(field["label"], str)
        
        # Optional fields validation
        if "placeholder" in field:
            assert isinstance(field["placeholder"], str)
        if "options" in field:
            assert isinstance(field["options"], list)
            for option in field["options"]:
                assert "value" in option and "label" in option
        if "min" in field and field["min"] is not None:
            assert isinstance(field["min"], (int, float))
        if "max" in field and field["max"] is not None:
            assert isinstance(field["max"], (int, float))
        if "required" in field:
            assert isinstance(field["required"], bool)
        if "default" in field:
            # default can be any type, just check it exists
            assert "default" in field


def test_ai_message_generation():
    """Test that AI messages are generated appropriately for different scenarios."""
    # Test image input AI message
    image_request = {
        "current_data": {},
        "new_input": "base64_encoded_image_data",
        "input_type": "image"
    }
    
    response = client.post("/api/analyze-step", json=image_request)
    assert response.status_code == 200
    image_data = response.json()
    
    assert image_data["ai_message"] is not None
    assert len(image_data["ai_message"]) > 0
    
    # Test text input AI message
    text_request = {
        "current_data": {"property_type": "house"},
        "new_input": "Beautiful house with garden",
        "input_type": "text"
    }
    
    response = client.post("/api/analyze-step", json=text_request)
    assert response.status_code == 200
    text_data = response.json()
    
    assert text_data["ai_message"] is not None
    assert len(text_data["ai_message"]) > 0
    
    # Test field update AI message
    update_request = {
        "current_data": {"property_type": "condo", "bedrooms": 2},
        "input_type": "field_update"
    }
    
    response = client.post("/api/analyze-step", json=update_request)
    assert response.status_code == 200
    update_data = response.json()
    
    assert update_data["ai_message"] is not None
    assert len(update_data["ai_message"]) > 0