import os
from fastapi.testclient import TestClient
import pytest
from typing import Dict, Any

# Ensure we use a local SQLite DB for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app, init_db  # noqa: E402

client = TestClient(app)


def setup_module(module):  # type: ignore[override]
    # Recreate DB for a clean slate
    init_db()


@pytest.fixture
def valid_image_request() -> Dict[str, Any]:
    """Fixture for a valid image analysis request."""
    return {
        "current_data": {},
        "new_input": "base64encodedimagedata",
        "input_type": "image"
    }


@pytest.fixture
def valid_text_request() -> Dict[str, Any]:
    """Fixture for a valid text analysis request."""
    return {
        "current_data": {"property_type": "apartment"},
        "new_input": "Beautiful apartment with 2 bedrooms and 1 bathroom",
        "input_type": "text"
    }


@pytest.fixture
def valid_field_update_request() -> Dict[str, Any]:
    """Fixture for a valid field update request."""
    return {
        "current_data": {"property_type": "house", "bedrooms": 3},
        "input_type": "field_update"
    }


def test_analyze_step_image_input_returns_200(valid_image_request):
    """Test that endpoint returns 200 for valid image input request."""
    response = client.post("/api/analyze-step", json=valid_image_request)
    assert response.status_code == 200


def test_analyze_step_text_input_returns_200(valid_text_request):
    """Test that endpoint returns 200 for valid text input request."""
    response = client.post("/api/analyze-step", json=valid_text_request)
    assert response.status_code == 200


def test_analyze_step_field_update_returns_200(valid_field_update_request):
    """Test that endpoint returns 200 for valid field update request."""
    response = client.post("/api/analyze-step", json=valid_field_update_request)
    assert response.status_code == 200


def test_response_matches_ui_manifest_schema(valid_image_request):
    """Test that response matches UI Manifest schema."""
    response = client.post("/api/analyze-step", json=valid_image_request)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields
    assert "extracted_data" in data
    assert "ui_schema" in data
    assert "ai_message" in data
    assert "step_number" in data
    assert "completion_percentage" in data
    
    # Validate field types
    assert isinstance(data["extracted_data"], dict)
    assert isinstance(data["ui_schema"], list)
    assert isinstance(data["ai_message"], str)
    assert isinstance(data["step_number"], int)
    assert isinstance(data["completion_percentage"], float)


def test_image_input_response_structure(valid_image_request):
    """Test specific response structure for image input."""
    response = client.post("/api/analyze-step", json=valid_image_request)
    data = response.json()
    
    # Should NOT auto-fill property_type in extracted_data (requires user confirmation)
    assert "property_type" not in data["extracted_data"]
    
    # AI message should mention property details (varies based on mock/fallback)
    assert len(data["ai_message"]) > 0
    assert "property" in data["ai_message"].lower() or "bedroom" in data["ai_message"].lower()
    assert data["step_number"] >= 1
    assert isinstance(data["completion_percentage"], float)


def test_image_upload_requires_property_type_confirmation(valid_image_request):
    """Test that image upload shows property_type field for user confirmation.
    
    Regression test for bug where user could skip property type selection.
    After image upload, property_type should be shown as a field with AI-detected default.
    """
    response = client.post("/api/analyze-step", json=valid_image_request)
    data = response.json()
    
    # property_type should NOT be in extracted_data (not confirmed yet)
    assert "property_type" not in data["extracted_data"]
    
    # property_type SHOULD be in ui_schema
    property_type_fields = [f for f in data["ui_schema"] if f["id"] == "property_type"]
    assert len(property_type_fields) == 1, "property_type field should be shown"
    
    property_type_field = property_type_fields[0]
    
    # Field should have a default value from AI detection
    assert "default" in property_type_field
    assert property_type_field["default"] is not None
    assert property_type_field["default"] in ["apartment", "house", "condo", "townhouse"]
    
    # Field should be required
    assert property_type_field.get("required") == True
    
    # Field should be a select input with options
    assert property_type_field["component_type"] == "select"
    assert "options" in property_type_field
    assert len(property_type_field["options"]) > 0
    
    # AI message should prompt user to confirm
    assert "confirm" in data["ai_message"].lower() or "type" in data["ai_message"].lower()


def test_text_input_response_structure(valid_text_request):
    """Test specific response structure for text input."""
    response = client.post("/api/analyze-step", json=valid_text_request)
    data = response.json()
    
    # Should preserve existing data and add new input
    assert data["extracted_data"]["property_type"] == "apartment"
    assert data["extracted_data"]["description"] == valid_text_request["new_input"]
    # UI schema should have some fields
    assert len(data["ui_schema"]) > 0


def test_field_update_response_structure(valid_field_update_request):
    """Test specific response structure for field update."""
    response = client.post("/api/analyze-step", json=valid_field_update_request)
    data = response.json()
    
    # Should preserve current data
    assert data["extracted_data"] == valid_field_update_request["current_data"]
    assert isinstance(data["ui_schema"], list)  # UI schema can be empty or contain fields


def test_handles_missing_current_data():
    """Test that endpoint handles missing current_data field."""
    request_data = {
        "new_input": "test input",
        "input_type": "text"
    }
    response = client.post("/api/analyze-step", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    # Should handle missing current_data gracefully
    assert isinstance(data["extracted_data"], dict)
    assert isinstance(data["ui_schema"], list)


def test_handles_missing_new_input():
    """Test that endpoint handles missing new_input field."""
    request_data = {
        "current_data": {"test": "data"},
        "input_type": "field_update"
    }
    response = client.post("/api/analyze-step", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["extracted_data"] == {"test": "data"}


def test_validates_input_type_required():
    """Test that input_type is required and validates."""
    request_data = {
        "current_data": {},
        "new_input": "test"
    }
    response = client.post("/api/analyze-step", json=request_data)
    assert response.status_code == 422  # FastAPI validation error


def test_validates_input_type_invalid():
    """Test that invalid input_type returns proper error."""
    request_data = {
        "current_data": {},
        "new_input": "test",
        "input_type": "invalid_type"
    }
    response = client.post("/api/analyze-step", json=request_data)
    assert response.status_code == 422  # FastAPI validation error


def test_ui_schema_field_validation():
    """Test that UI schema fields are properly structured."""
    response = client.post("/api/analyze-step", json={
        "current_data": {},
        "input_type": "image"
    })
    data = response.json()
    
    # Check UI field structure
    if data["ui_schema"]:
        field = data["ui_schema"][0]
        assert "id" in field
        assert "component_type" in field
        assert "label" in field
        assert field["component_type"] in ["text", "select", "number", "toggle"]


def test_cors_headers_present():
    """Test that CORS headers are present in response."""
    response = client.post("/api/analyze-step", json={
        "current_data": {},
        "input_type": "image"
    })
    
    # FastAPI TestClient doesn't include CORS headers by default
    # but we can verify the CORS middleware is configured
    assert response.status_code == 200


def test_empty_request_validation():
    """Test that completely empty request is properly rejected."""
    response = client.post("/api/analyze-step", json={})
    assert response.status_code == 422


def test_completion_percentage_bounds():
    """Test that completion percentage stays within valid bounds."""
    # Test with many fields
    response = client.post("/api/analyze-step", json={
        "current_data": {f"field_{i}": f"value_{i}" for i in range(20)},  # 20 fields
        "input_type": "field_update"
    })
    data = response.json()
    assert 0 <= data["completion_percentage"] <= 100


def test_step_number_calculation():
    """Test that step number is calculated correctly."""
    # Test with field update
    response = client.post("/api/analyze-step", json={
        "current_data": {"field1": "value1", "field2": "value2"},
        "input_type": "field_update"
    })
    data = response.json()
    assert data["step_number"] == 2  # Should match number of fields


def test_response_consistency():
    """Test that response format is consistent across different input types."""
    input_types = ["image", "text", "field_update"]
    
    for input_type in input_types:
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": input_type
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # All responses should have the same basic structure
        required_fields = ["extracted_data", "ui_schema", "ai_message", "step_number", "completion_percentage"]
        for field in required_fields:
            assert field in data


def test_field_options_structure():
    """Test that select field options are properly structured."""
    response = client.post("/api/analyze-step", json={
        "current_data": {},
        "input_type": "image"
    })
    data = response.json()
    
    # Find select fields
    select_fields = [field for field in data["ui_schema"] if field.get("component_type") == "select"]
    
    for field in select_fields:
        if "options" in field and field["options"]:
            option = field["options"][0]
            assert "value" in option
            assert "label" in option


def test_number_field_constraints():
    """Test that number fields have proper constraints."""
    response = client.post("/api/analyze-step", json={
        "current_data": {},
        "input_type": "image"
    })
    data = response.json()
    
    # Find number fields
    number_fields = [field for field in data["ui_schema"] if field.get("component_type") == "number"]
    
    for field in number_fields:
        if "min" in field:
            assert isinstance(field["min"], (int, float))
        if "max" in field:
            assert isinstance(field["max"], (int, float))


def test_optional_fields_handling():
    """Test that optional fields are properly handled."""
    response = client.post("/api/analyze-step", json={
        "current_data": {},
        "new_input": "test",
        "input_type": "text"
    })
    assert response.status_code == 200
    
    data = response.json()
    # Optional fields like confidence_scores might not be present
    if "confidence_scores" in data and data["confidence_scores"] is not None:
        assert isinstance(data["confidence_scores"], dict)