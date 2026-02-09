"""
Tests for the property feature extraction logic.
"""

import pytest
from app.feature_extractor import PropertyFeatureExtractor, extract_features, ExtractedFeatures


class TestPropertyFeatureExtractor:
    """Test cases for PropertyFeatureExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PropertyFeatureExtractor()
    
    def test_extract_property_type_apartment(self):
        """Test extraction of apartment property type."""
        description = "This is a beautiful modern apartment with 2 bedrooms"
        features = self.extractor.extract_features(description)
        
        assert features.property_type == 'apartment'
        assert features.property_type_confidence > 0
    
    def test_extract_property_type_house(self):
        """Test extraction of house property type."""
        description = "Spacious single family house with large backyard"
        features = self.extractor.extract_features(description)
        
        assert features.property_type == 'house'
        assert features.property_type_confidence > 0
    
    def test_extract_property_type_townhouse(self):
        """Test extraction of townhouse property type."""
        description = "Lovely townhouse in quiet neighborhood"
        features = self.extractor.extract_features(description)
        
        assert features.property_type == 'townhouse'
        assert features.property_type_confidence > 0
    
    def test_extract_multiple_amenities(self):
        """Test extraction of multiple amenities."""
        description = "Home features pool, garage, balcony, and fireplace"
        features = self.extractor.extract_features(description)
        
        assert 'pool' in features.amenities
        assert 'garage' in features.amenities
        assert 'balcony' in features.amenities
        assert 'fireplace' in features.amenities
        assert len(features.amenities) >= 4
        assert len(features.amenities_confidence) >= 4
    
    def test_extract_style_modern(self):
        """Test extraction of modern style."""
        description = "Sleek modern design with clean lines and contemporary finishes"
        features = self.extractor.extract_features(description)
        
        assert features.style == 'modern'
        assert features.style_confidence > 0
    
    def test_extract_style_traditional(self):
        """Test extraction of traditional style."""
        description = "Traditional colonial home with classic features"
        features = self.extractor.extract_features(description)
        
        assert features.style == 'traditional'
        assert features.style_confidence > 0
    
    def test_extract_rooms_bedrooms(self):
        """Test extraction of bedroom count."""
        description = "This house has 3 bedrooms and 2 bathrooms"
        features = self.extractor.extract_features(description)
        
        assert 'bedroom' in features.rooms
        assert features.rooms['bedroom'] == 3
        assert 'bathroom' in features.rooms
        assert features.rooms['bathroom'] == 2
    
    def test_extract_materials(self):
        """Test extraction of materials."""
        description = "Features hardwood floors and granite countertops"
        features = self.extractor.extract_features(description)
        
        assert 'hardwood_floors' in features.materials
        assert 'granite_counters' in features.materials
        assert len(features.materials) >= 2
    
    def test_empty_description(self):
        """Test handling of empty description."""
        features = self.extractor.extract_features("")
        
        assert features.property_type is None
        assert features.property_type_confidence == 0.0
        assert len(features.amenities) == 0
        assert features.style is None
        assert features.style_confidence == 0.0
    
    def test_no_features_found(self):
        """Test handling when no features are found."""
        description = "This is a nice place"
        features = self.extractor.extract_features(description)
        
        # Should handle gracefully without errors
        assert isinstance(features, ExtractedFeatures)
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary format."""
        description = "Modern apartment with pool and garage"
        features = self.extractor.extract_features(description)
        result_dict = self.extractor.to_dict(features)
        
        assert isinstance(result_dict, dict)
        assert 'property_type' in result_dict
        assert 'amenities' in result_dict
        assert 'style' in result_dict
        assert 'rooms' in result_dict
        assert 'materials' in result_dict
        assert 'property_type_confidence' in result_dict
    
    def test_confidence_scores_range(self):
        """Test that confidence scores are within valid range."""
        description = "Beautiful modern apartment with granite countertops"
        features = self.extractor.extract_features(description)
        
        # Check all confidence scores are between 0 and 1
        assert 0 <= features.property_type_confidence <= 1
        assert 0 <= features.style_confidence <= 1
        for confidence in features.amenities_confidence.values():
            assert 0 <= confidence <= 1
        for confidence in features.rooms_confidence.values():
            assert 0 <= confidence <= 1
        for confidence in features.materials_confidence.values():
            assert 0 <= confidence <= 1


class TestConvenienceFunction:
    """Test cases for the convenience extract_features function."""
    
    def test_extract_features_function(self):
        """Test the convenience function."""
        description = "Modern house with 3 bedrooms, pool, and garage"
        result = extract_features(description)
        
        assert isinstance(result, dict)
        assert 'property_type' in result
        assert 'amenities' in result
        assert 'style' in result
        assert 'rooms' in result
        assert 'materials' in result
    
    def test_extract_features_empty(self):
        """Test convenience function with empty input."""
        result = extract_features("")
        
        assert isinstance(result, dict)
        assert result['property_type'] is None
        assert len(result['amenities']) == 0


class TestRealWorldExamples:
    """Test cases with realistic property descriptions."""
    
    def test_luxury_apartment(self):
        """Test extraction from luxury apartment description."""
        description = ("Stunning luxury apartment featuring modern design with floor-to-ceiling windows, "
                        "hardwood floors throughout, granite countertops in gourmet kitchen, "
                        "2 bedrooms including master suite with walk-in closet, 2 full bathrooms, "
                        "in-unit washer/dryer, central air conditioning, and access to building "
                        "amenities including pool, fitness center, and 24-hour concierge service.")
        
        features = extract_features(description)
        
        assert features['property_type'] == 'apartment'
        assert 'hardwood_floors' in features['materials']
        assert 'granite_counters' in features['materials']
        assert features['rooms']['bedroom'] == 2
        assert features['rooms']['bathroom'] == 2
        assert 'pool' in features['amenities']
        assert 'gym' in features['amenities']
        assert features['style'] == 'modern'
    
    def test_suburban_house(self):
        """Test extraction from suburban house description."""
        description = ("Charming 4-bedroom colonial house with traditional styling, "
                        "hardwood floors in living areas, updated kitchen with stainless steel appliances, "
                        "formal dining room, family room with fireplace, "
                        "finished basement, attached 2-car garage, "
                        "large backyard with deck and mature trees.")
        
        features = extract_features(description)
        
        assert features['property_type'] == 'house'
        assert features['style'] == 'traditional'
        assert features['rooms']['bedroom'] == 4
        assert 'hardwood_floors' in features['materials']
        assert 'stainless_steel' in features['materials']
        assert 'fireplace' in features['amenities']
        assert 'garage' in features['amenities']
        assert 'deck' in features['amenities']
    
    def test_townhouse_description(self):
        """Test extraction from townhouse description."""
        description = ("Well-maintained 3-bedroom, 2.5-bathroom townhouse with contemporary design, "
                        "open concept living area, kitchen with granite counters, "
                        "master suite with walk-in closet, balcony off master bedroom, "
                        "attached garage, community pool and fitness center.")
        
        features = extract_features(description)
        
        assert features['property_type'] == 'townhouse'
        assert features['rooms']['bedroom'] == 3
        assert 'granite_counters' in features['materials']
        assert 'balcony' in features['amenities']
        assert 'garage' in features['amenities']
        assert 'pool' in features['amenities']


if __name__ == "__main__":
    pytest.main([__file__])