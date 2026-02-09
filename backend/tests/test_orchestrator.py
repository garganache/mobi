"""
Tests for the field orchestration logic.
"""

import pytest
from app.orchestrator import orchestrator, PROPERTY_TYPE_FIELDS, COMMON_FIELDS
from app.schemas import UIField


class TestFieldOrchestrator:
    """Test cases for the FieldOrchestrator class."""
    
    def test_get_next_fields_no_property_type(self):
        """Test that property_type is the first field when not provided."""
        current_data = {}
        next_fields = orchestrator.get_next_fields(current_data)
        
        assert len(next_fields) == 1
        assert next_fields[0].id == "property_type"
        assert next_fields[0].component_type == "select"
        assert next_fields[0].required is True
    
    def test_get_next_fields_apartment(self):
        """Test fields for apartment property type."""
        current_data = {"property_type": "apartment"}
        next_fields = orchestrator.get_next_fields(current_data)
        
        # Should get 3 fields max (bedrooms, bathrooms, square_feet based on priority)
        assert len(next_fields) <= 3
        
        # Check that we get the common fields first (based on priority)
        field_ids = [field.id for field in next_fields]
        assert "bedrooms" in field_ids
        assert "bathrooms" in field_ids
    
    def test_get_next_fields_house(self):
        """Test fields for house property type."""
        current_data = {"property_type": "house"}
        next_fields = orchestrator.get_next_fields(current_data)
        
        # Should get common fields first
        field_ids = [field.id for field in next_fields]
        assert "bedrooms" in field_ids
        assert "bathrooms" in field_ids
    
    def test_get_next_fields_with_partial_data(self):
        """Test that filled fields are not returned."""
        current_data = {
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1
        }
        next_fields = orchestrator.get_next_fields(current_data)
        
        field_ids = [field.id for field in next_fields]
        assert "bedrooms" not in field_ids
        assert "bathrooms" not in field_ids
        assert "square_feet" in field_ids  # Should be next based on priority
    
    def test_max_fields_per_step(self):
        """Test that we limit fields to max_fields_per_step."""
        current_data = {"property_type": "house"}
        next_fields = orchestrator.get_next_fields(current_data)
        
        assert len(next_fields) <= orchestrator.max_fields_per_step
    
    def test_prioritize_fields(self):
        """Test field prioritization logic."""
        unfilled_fields = [
            {"id": "field_a", "priority": 5},
            {"id": "field_b", "priority": 1},
            {"id": "field_c", "priority": 3}
        ]
        current_data = {}
        
        prioritized = orchestrator._prioritize_fields(unfilled_fields, current_data)
        
        # Should be sorted by priority (lower number first)
        assert prioritized[0]["id"] == "field_b"
        assert prioritized[1]["id"] == "field_c"
        assert prioritized[2]["id"] == "field_a"
    
    def test_generate_ai_message_no_property_type(self):
        """Test AI message when property_type is missing."""
        current_data = {}
        next_fields = orchestrator.get_next_fields(current_data)
        message = orchestrator.generate_ai_message(current_data, next_fields)
        
        assert "type of property" in message.lower()
    
    def test_generate_ai_message_apartment(self):
        """Test AI message for apartment."""
        current_data = {"property_type": "apartment"}
        next_fields = orchestrator.get_next_fields(current_data)
        message = orchestrator.generate_ai_message(current_data, next_fields)
        
        assert "apartment" in message.lower()
    
    def test_generate_ai_message_house(self):
        """Test AI message for house."""
        current_data = {"property_type": "house"}
        next_fields = orchestrator.get_next_fields(current_data)
        message = orchestrator.generate_ai_message(current_data, next_fields)
        
        assert "house" in message.lower()
    
    def test_calculate_completion_percentage(self):
        """Test completion percentage calculation."""
        # Empty state
        current_data = {}
        percentage = orchestrator.calculate_completion_percentage(current_data)
        assert percentage == 0.0
        
        # Partial state
        current_data = {"property_type": "apartment", "bedrooms": 2}
        percentage = orchestrator.calculate_completion_percentage(current_data)
        assert percentage > 0.0
        assert percentage <= 100.0
        
        # Complete state (simulated)
        current_data = {
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "square_feet": 1000,
            "price": 300000,
            "address": "123 Main St",
            "description": "Nice apartment",
            "has_parking": True,
            "has_pool": False,
            "floor_number": 5,
            "elevator": True,
            "building_age": 10,
            "pets_allowed": True
        }
        percentage = orchestrator.calculate_completion_percentage(current_data)
        assert percentage == 100.0
    
    def test_property_type_fields_exist(self):
        """Test that property type fields are properly configured."""
        assert "house" in PROPERTY_TYPE_FIELDS
        assert "apartment" in PROPERTY_TYPE_FIELDS
        assert "condo" in PROPERTY_TYPE_FIELDS
        
        # Check that fields have required attributes
        for property_type, fields in PROPERTY_TYPE_FIELDS.items():
            for field in fields:
                assert "id" in field
                assert "component_type" in field
                assert "label" in field
    
    def test_common_fields_exist(self):
        """Test that common fields are properly configured."""
        assert len(COMMON_FIELDS) > 0
        
        for field in COMMON_FIELDS:
            assert "id" in field
            assert "component_type" in field
            assert "label" in field
            assert "priority" in field