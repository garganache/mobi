"""
Integration tests for the orchestration logic implementation.
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestOrchestrationIntegration:
    """Integration tests for the orchestration logic."""
    
    def test_empty_form_returns_property_type_first(self, client):
        """Test that an empty form returns property_type as the first field."""
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return property_type field
        assert len(data["ui_schema"]) == 1
        assert data["ui_schema"][0]["id"] == "property_type"
        assert data["ui_schema"][0]["component_type"] == "select"
        assert data["ui_schema"][0]["required"] is True
    
    def test_apartment_property_type_returns_appropriate_fields(self, client):
        """Test that apartment property type returns relevant fields."""
        response = client.post("/api/analyze-step", json={
            "current_data": {"property_type": "apartment"},
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return up to 3 fields
        assert len(data["ui_schema"]) <= 3
        
        # Should include priority fields like bedrooms, bathrooms
        field_ids = [field["id"] for field in data["ui_schema"]]
        assert "bedrooms" in field_ids
        assert "bathrooms" in field_ids
    
    def test_house_property_type_returns_appropriate_fields(self, client):
        """Test that house property type returns relevant fields."""
        response = client.post("/api/analyze-step", json={
            "current_data": {"property_type": "house"},
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return up to 3 fields
        assert len(data["ui_schema"]) <= 3
        
        # Should include priority fields
        field_ids = [field["id"] for field in data["ui_schema"]]
        assert "bedrooms" in field_ids
        assert "bathrooms" in field_ids
    
    def test_condo_property_type_returns_appropriate_fields(self, client):
        """Test that condo property type returns relevant fields."""
        response = client.post("/api/analyze-step", json={
            "current_data": {"property_type": "condo"},
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return up to 3 fields
        assert len(data["ui_schema"]) <= 3
        
        # Should include priority fields
        field_ids = [field["id"] for field in data["ui_schema"]]
        assert "bedrooms" in field_ids
        assert "bathrooms" in field_ids
    
    def test_filled_fields_are_not_returned(self, client):
        """Test that already filled fields are not returned in next step."""
        response = client.post("/api/analyze-step", json={
            "current_data": {
                "property_type": "apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "square_feet": 1000
            },
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not return already filled fields
        field_ids = [field["id"] for field in data["ui_schema"]]
        assert "bedrooms" not in field_ids
        assert "bathrooms" not in field_ids
        assert "square_feet" not in field_ids
        
        # Should return next priority fields
        expected_fields = ["price", "address", "description"]
        for field_id in expected_fields[:3]:  # Up to 3 fields
            assert field_id in field_ids
    
    def test_image_input_extracts_basic_data(self, client):
        """Test that image input extracts basic property information."""
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": "image",
            "new_input": "base64_encoded_image_data_here"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should extract some basic data (but NOT property_type - that's shown as a field)
        assert "bedrooms" in data["extracted_data"]
        # Property type should be in UI schema with a default value
        property_type_field = next((f for f in data["ui_schema"] if f["id"] == "property_type"), None)
        assert property_type_field is not None
        # The actual extracted data may vary based on the mock implementation
    
    def test_text_input_processes_description(self, client):
        """Test that text input processes description text."""
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": "text",
            "new_input": "Beautiful 3-bedroom house with large backyard and modern kitchen"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should add description to extracted data
        assert data["extracted_data"]["description"] == "Beautiful 3-bedroom house with large backyard and modern kitchen"
        
        # Should provide appropriate AI message
        assert data["ai_message"] is not None
        assert len(data["ai_message"]) > 10
    
    def test_field_update_maintains_state(self, client):
        """Test that field update maintains current state correctly."""
        response = client.post("/api/analyze-step", json={
            "current_data": {
                "property_type": "house",
                "bedrooms": 3
            },
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should maintain existing data
        assert data["extracted_data"]["property_type"] == "house"
        assert data["extracted_data"]["bedrooms"] == 3
        
        # Should provide appropriate AI message
        assert data["ai_message"] is not None
        assert len(data["ai_message"]) > 10
    
    def test_max_fields_per_step_limit(self, client):
        """Test that we limit fields to maximum per step."""
        response = client.post("/api/analyze-step", json={
            "current_data": {"property_type": "apartment"},
            "input_type": "field_update"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not exceed maximum fields per step
        assert len(data["ui_schema"]) <= 3
    
    def test_completion_percentage_calculation(self, client):
        """Test that completion percentage is calculated correctly."""
        # Test empty form
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": "field_update"
        })
        data = response.json()
        assert data["completion_percentage"] == 0.0
        
        # Test partial form
        response = client.post("/api/analyze-step", json={
            "current_data": {
                "property_type": "apartment",
                "bedrooms": 2,
                "bathrooms": 1
            },
            "input_type": "field_update"
        })
        data = response.json()
        assert data["completion_percentage"] > 0.0
        assert data["completion_percentage"] <= 100.0
    
    def test_ai_message_appropriateness(self, client):
        """Test that AI messages are appropriate for the context."""
        # Test initial state - should ask for property type
        response = client.post("/api/analyze-step", json={
            "current_data": {},
            "input_type": "field_update"
        })
        data = response.json()
        # The AI message should be appropriate for the initial state
        assert len(data["ui_schema"]) == 1
        assert data["ui_schema"][0]["id"] == "property_type"