"""
Tests for multi-image analysis functionality.
"""

import pytest
from unittest.mock import Mock, patch
from app.vision_model import (
    analyze_multiple_images,
    synthesize_property_overview,
    generate_unified_description,
    determine_overall_condition
)


class TestAnalyzeMultipleImages:
    """Test the analyze_multiple_images function."""
    
    def test_analyze_multiple_images_with_mock_model(self):
        """Test analyzing multiple images with mock model."""
        # Create mock image data
        images = [b"fake_image_data_1", b"fake_image_data_2", b"fake_image_data_3"]
        
        result = analyze_multiple_images(images, model_type="mock")
        
        # Verify structure
        assert "individual_analyses" in result
        assert "synthesis" in result
        assert len(result["individual_analyses"]) == 3
        
        # Verify each analysis has required fields
        for analysis in result["individual_analyses"]:
            assert "description" in analysis
            assert "property_type" in analysis
            assert "rooms" in analysis
            assert "amenities" in analysis
            assert "image_index" in analysis
        
        # Verify synthesis
        synthesis = result["synthesis"]
        assert "total_rooms" in synthesis
        assert "room_breakdown" in synthesis
        assert "amenities_by_room" in synthesis
        assert "unified_description" in synthesis
        assert "property_overview" in synthesis
    
    def test_analyze_multiple_images_with_failed_analysis(self):
        """Test handling of failed individual analyses."""
        images = [b"fake_image_data"]
        
        with patch('app.vision_model.analyze_property_image') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")
            
            result = analyze_multiple_images(images, model_type="mock")
            
            # Should still return result with error handling
            assert len(result["individual_analyses"]) == 1
            analysis = result["individual_analyses"][0]
            assert "error" in analysis
            assert analysis["property_type"] == "unknown"
    
    def test_analyze_multiple_images_empty_list(self):
        """Test with empty image list."""
        result = analyze_multiple_images([], model_type="mock")
        
        assert len(result["individual_analyses"]) == 0
        assert result["synthesis"]["total_rooms"] == 0
        assert "No images analyzed" in result["synthesis"]["unified_description"]


class TestSynthesizePropertyOverview:
    """Test the synthesize_property_overview function."""
    
    def test_synthesize_single_room(self):
        """Test synthesis with a single room analysis."""
        analyses = [
            {
                "description": "A modern kitchen with granite countertops",
                "property_type": "apartment",
                "rooms": {"kitchen": 1},
                "amenities": ["granite_counters", "stainless_steel"],
                "style": "modern",
                "materials": ["granite_counters", "stainless_steel"],
                "condition": "excellent"
            }
        ]
        
        result = synthesize_property_overview(analyses)
        
        assert result["total_rooms"] == 1
        assert result["room_breakdown"]["kitchen"] == 1
        # Check amenities are in property overview common_amenities
        assert "granite_counters" in result["property_overview"]["common_amenities"]
        assert "stainless_steel" in result["property_overview"]["common_amenities"]
        assert "apartment" in result["property_overview"]["property_type"]
        assert "modern" in result["property_overview"]["style"]
    
    def test_synthesize_multiple_rooms(self):
        """Test synthesis with multiple rooms."""
        analyses = [
            {
                "description": "A bedroom with hardwood floors",
                "property_type": "apartment",
                "rooms": {"bedroom": 1},
                "amenities": ["hardwood_floors"],
                "style": "modern",
                "materials": ["hardwood_floors"],
                "condition": "good"
            },
            {
                "description": "A kitchen with granite counters",
                "property_type": "apartment",
                "rooms": {"kitchen": 1},
                "amenities": ["granite_counters", "stainless_steel"],
                "style": "modern",
                "materials": ["granite_counters", "stainless_steel"],
                "condition": "excellent"
            }
        ]
        
        result = synthesize_property_overview(analyses)
        
        assert result["total_rooms"] == 2
        assert result["room_breakdown"]["bedroom"] == 1
        assert result["room_breakdown"]["kitchen"] == 1
        # Check amenities are aggregated in property overview
        assert "hardwood_floors" in result["property_overview"]["common_amenities"]
        assert "granite_counters" in result["property_overview"]["common_amenities"]
        assert "apartment" in result["property_overview"]["property_type"]
    
    def test_synthesize_duplicate_rooms(self):
        """Test synthesis with duplicate room types across images."""
        analyses = [
            {
                "description": "First bedroom",
                "property_type": "apartment",
                "rooms": {"bedroom": 1},
                "amenities": ["hardwood_floors"],
                "style": "modern",
                "materials": ["hardwood_floors"],
                "condition": "good"
            },
            {
                "description": "Second bedroom",
                "property_type": "apartment",
                "rooms": {"bedroom": 1},
                "amenities": ["carpet"],
                "style": "modern",
                "materials": ["carpet"],
                "condition": "good"
            }
        ]
        
        result = synthesize_property_overview(analyses)
        
        assert result["total_rooms"] == 2
        assert result["room_breakdown"]["bedroom"] == 2  # Should sum up
    
    def test_synthesize_empty_analyses(self):
        """Test synthesis with empty analyses list."""
        result = synthesize_property_overview([])
        
        assert result["total_rooms"] == 0
        assert result["room_breakdown"] == {}
        assert "No images analyzed" in result["unified_description"]


class TestGenerateUnifiedDescription:
    """Test the generate_unified_description function."""
    
    def test_generate_single_room_description(self):
        """Test description generation for single room (now in Romanian)."""
        description = generate_unified_description(
            total_rooms=1,
            room_breakdown={"kitchen": 1},
            amenities=["granite_counters"],
            materials=["granite_counters"],
            property_type="apartment",
            style="modern",
            analyses=[]
        )
        
        # Check for Romanian terminology: Bucătărie, apartament, modern
        assert len(description) > 20
        assert any(word in description.lower() for word in ["bucătărie", "kitchen"])
        assert any(word in description.lower() for word in ["apartament", "apartment"])
        assert "modern" in description.lower()
        assert description.endswith(".")
    
    def test_generate_multiple_rooms_description(self):
        """Test description generation for multiple rooms (now in Romanian)."""
        description = generate_unified_description(
            total_rooms=3,
            room_breakdown={"bedroom": 2, "kitchen": 1},
            amenities=["hardwood_floors"],
            materials=["hardwood_floors"],
            property_type="house",
            style="traditional",
            analyses=[]
        )
        
        # Check for meaningful description with Romanian or English terms
        assert len(description) > 30
        assert any(word in description.lower() for word in ["dormitor", "bedroom"])
        assert any(word in description.lower() for word in ["bucătărie", "kitchen"])
        assert any(word in description.lower() for word in ["casă", "house"])
        assert any(word in description.lower() for word in ["tradițional", "traditional"])
    
    def test_generate_hardwood_throughout_pattern(self):
        """Test detection of hardwood floors throughout (now in Romanian)."""
        analyses = [
            {"amenities": ["hardwood_floors"]},
            {"amenities": ["hardwood_floors"]},
            {"amenities": ["hardwood_floors"]}
        ]
        
        description = generate_unified_description(
            total_rooms=3,
            room_breakdown={"bedroom": 3},
            amenities=["hardwood_floors"],
            materials=["hardwood_floors"],
            property_type="apartment",
            style="modern",
            analyses=analyses
        )
        
        # Check for hardwood mention in Romanian or English
        assert any(phrase in description.lower() for phrase in ["parchet", "hardwood"])
    
    def test_generate_with_common_amenities(self):
        """Test description with common amenities (now in Romanian)."""
        description = generate_unified_description(
            total_rooms=2,
            room_breakdown={"kitchen": 1, "living_room": 1},
            amenities=["granite_counters", "stainless_steel", "fireplace"],
            materials=["granite_counters", "stainless_steel"],
            property_type="apartment",
            style="modern",
            analyses=[]
        )
        
        # Check for amenity mentions in Romanian or English
        assert any(phrase in description.lower() for phrase in ["granit", "granite"])
        assert any(phrase in description.lower() for phrase in ["oțel inoxidabil", "stainless steel"])
        assert any(phrase in description.lower() for phrase in ["șemineu", "fireplace"])


class TestDetermineOverallCondition:
    """Test the determine_overall_condition function."""
    
    def test_single_condition(self):
        """Test with all analyses having same condition."""
        analyses = [
            {"condition": "excellent"},
            {"condition": "excellent"},
            {"condition": "excellent"}
        ]
        
        condition = determine_overall_condition(analyses)
        assert condition == "excellent"
    
    def test_mixed_conditions(self):
        """Test with analyses having different conditions."""
        analyses = [
            {"condition": "excellent"},
            {"condition": "good"},
            {"condition": "fair"}
        ]
        
        condition = determine_overall_condition(analyses)
        assert condition == "mixed"
    
    def test_unknown_conditions(self):
        """Test with missing condition fields."""
        analyses = [
            {"condition": "excellent"},
            {},  # No condition field
            {"condition": "excellent"}
        ]
        
        condition = determine_overall_condition(analyses)
        assert condition == "mixed"
    
    def test_empty_analyses(self):
        """Test with empty analyses list."""
        condition = determine_overall_condition([])
        assert condition == "unknown"


class TestIntegration:
    """Integration tests for multi-image analysis."""
    
    def test_full_multi_image_workflow(self):
        """Test complete multi-image analysis workflow."""
        # Create mock image data for different room types
        images = [
            b"kitchen_image_data",
            b"bedroom_image_data", 
            b"living_room_image_data"
        ]
        
        result = analyze_multiple_images(images, model_type="mock")
        
        # Verify complete structure
        assert "individual_analyses" in result
        assert "synthesis" in result
        
        synthesis = result["synthesis"]
        assert "total_rooms" in synthesis
        assert "room_breakdown" in synthesis
        assert "amenities_by_room" in synthesis
        assert "unified_description" in synthesis
        assert "property_overview" in synthesis
        
        # Verify unified description is coherent
        unified_description = synthesis["unified_description"]
        assert len(unified_description) > 20  # Should be substantial
        assert unified_description.endswith(".")
        
        # Verify property overview
        overview = synthesis["property_overview"]
        assert "property_type" in overview
        assert "style" in overview
        assert "total_rooms" in overview
        assert "room_breakdown" in overview
        assert "common_amenities" in overview
        assert "common_materials" in overview
        assert "condition" in overview