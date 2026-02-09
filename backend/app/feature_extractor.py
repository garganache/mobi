"""
Feature extraction logic for property data from vision model outputs.

This module processes natural language descriptions from vision models and extracts
structured property features including property type, amenities, style, rooms, and materials.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFeatures:
    """Container for extracted property features with confidence scores."""
    property_type: Optional[str] = None
    property_type_confidence: float = 0.0
    amenities: List[str] = None
    amenities_confidence: Dict[str, float] = None
    style: Optional[str] = None
    style_confidence: float = 0.0
    rooms: Dict[str, int] = None
    rooms_confidence: Dict[str, float] = None
    materials: List[str] = None
    materials_confidence: Dict[str, float] = None
    
    def __post_init__(self):
        if self.amenities is None:
            self.amenities = []
        if self.amenities_confidence is None:
            self.amenities_confidence = {}
        if self.rooms is None:
            self.rooms = {}
        if self.rooms_confidence is None:
            self.rooms_confidence = {}
        if self.materials is None:
            self.materials = []
        if self.materials_confidence is None:
            self.materials_confidence = {}


class PropertyFeatureExtractor:
    """
    Extracts structured property features from vision model descriptions.
    
    This class processes natural language descriptions and converts them into
    structured data suitable for real estate listing forms.
    """
    
    def __init__(self):
        # Property type mappings
        self.property_types = {
            'apartment': ['apartment', 'apt', 'flat', 'condo', 'condominium', 'studio', 'loft'],
            'house': ['house', 'home', 'residence', 'dwelling', 'single family', 'single-family'],
            'townhouse': ['townhouse', 'townhome', 'row house', 'rowhouse', 'attached'],
            'land': ['land', 'lot', 'plot', 'acreage', 'parcel', 'vacant land'],
            'mobile': ['mobile', 'manufactured', 'trailer', 'rv'],
            'multi_family': ['multi-family', 'duplex', 'triplex', 'fourplex', 'apartment building']
        }
        
        # Amenity mappings
        self.amenities = {
            'pool': ['pool', 'swimming pool', 'lap pool', 'infinity pool', 'pool area'],
            'garage': ['garage', 'carport', 'parking space', 'attached garage', 'detached garage'],
            'balcony': ['balcony', 'balconies', 'terrace', 'patio', 'veranda'],
            'fireplace': ['fireplace', 'fire place', 'wood burning', 'gas fireplace'],
            'deck': ['deck', 'wood deck', 'composite deck', 'decking'],
            'garden': ['garden', 'yard', 'backyard', 'front yard', 'lawn'],
            'hot_tub': ['hot tub', 'jacuzzi', 'spa', 'whirlpool'],
            'gym': ['gym', 'fitness', 'exercise room', 'workout room', 'home gym'],
            'elevator': ['elevator', 'lift', 'wheelchair access', 'handicap access'],
            'security': ['security', 'alarm', 'camera', 'cameras', 'security system'],
            'air_conditioning': ['air conditioning', 'ac', 'central air', 'hvac', 'climate control'],
            'heating': ['heating', 'central heating', 'forced air', 'radiator'],
            'dishwasher': ['dishwasher', 'dish washer', 'stainless appliances'],
            'washer': ['washer', 'washing machine', 'laundry', 'laundry room'],
            'dryer': ['dryer', 'clothes dryer', 'laundry'],
            'refrigerator': ['refrigerator', 'fridge', 'stainless steel appliances'],
            'stove': ['stove', 'range', 'oven', 'cooktop'],
            'microwave': ['microwave', 'microwave oven'],
            'disposal': ['garbage disposal', 'waste disposal'],
            'hardwood_floors': ['hardwood', 'hard wood', 'wood floors', 'hardwood floors'],
            'granite_counters': ['granite', 'granite counters', 'granite countertops'],
            'walk_in_closet': ['walk-in closet', 'walk in closet', 'large closet'],
            'vaulted_ceiling': ['vaulted ceiling', 'high ceiling', 'cathedral ceiling'],
            'skylight': ['skylight', 'skylights', 'roof window'],
            'french_doors': ['french doors', 'patio doors', 'sliding doors']
        }
        
        # Style mappings
        self.styles = {
            'modern': ['modern', 'contemporary', 'sleek', 'minimalist', 'clean lines'],
            'traditional': ['traditional', 'classic', 'colonial', 'timeless', 'conventional'],
            'rustic': ['rustic', 'country', 'farmhouse', 'cabin', 'log', 'woodsy'],
            'victorian': ['victorian', 'ornate', 'detailed', 'gingerbread'],
            'craftsman': ['craftsman', 'bungalow', 'arts and crafts', 'mission style'],
            'mediterranean': ['mediterranean', 'spanish', 'tuscan', 'stucco', 'tile roof'],
            'cape_cod': ['cape cod', 'cape', 'new england'],
            'ranch': ['ranch', 'rambler', 'single story', 'one story'],
            'split_level': ['split level', 'tri-level', 'bi-level'],
            'two_story': ['two story', '2-story', 'colonial']
        }
        
        # Room mappings
        self.rooms = {
            'bedroom': ['bedroom', 'bedrooms', 'bed', 'master bedroom', 'guest room'],
            'bathroom': ['bathroom', 'bathrooms', 'bath', 'powder room', 'half bath', 'full bath'],
            'kitchen': ['kitchen', 'eat-in kitchen', 'gourmet kitchen', 'chef kitchen'],
            'living_room': ['living room', 'living area', 'great room', 'family room'],
            'dining_room': ['dining room', 'dining area', 'formal dining'],
            'office': ['office', 'study', 'den', 'library', 'work room'],
            'basement': ['basement', 'finished basement', 'unfinished basement'],
            'attic': ['attic', 'loft', 'bonus room'],
            'garage': ['garage', 'garage space'],
            'laundry_room': ['laundry room', 'utility room', 'mud room']
        }
        
        # Material mappings
        self.materials = {
            'hardwood_floors': ['hardwood floors', 'wood floors', 'hardwood flooring'],
            'granite_counters': ['granite countertops', 'granite counters', 'granite'],
            'stainless_steel': ['stainless steel', 'stainless appliances', 'stainless'],
            'tile': ['tile', 'ceramic tile', 'porcelain tile', 'stone tile'],
            'carpet': ['carpet', 'carpeting', 'wall-to-wall carpet'],
            'laminate': ['laminate', 'laminate flooring'],
            'vinyl': ['vinyl', 'vinyl flooring', 'luxury vinyl'],
            'marble': ['marble', 'marble counters', 'marble floors'],
            'quartz': ['quartz', 'quartz countertops'],
            'brick': ['brick', 'brick exterior', 'brick wall'],
            'stone': ['stone', 'stone exterior', 'natural stone'],
            'stucco': ['stucco', 'stucco exterior'],
            'vinyl_siding': ['vinyl siding', 'siding'],
            'wood_siding': ['wood siding', 'cedar siding', 'shingles']
        }
    
    def extract_features(self, description: str) -> ExtractedFeatures:
        """
        Extract property features from a natural language description.
        
        Args:
            description: Natural language description from vision model
            
        Returns:
            ExtractedFeatures object containing structured property data
        """
        if not description:
            logger.warning("Empty description provided")
            return ExtractedFeatures()
        
        description_lower = description.lower()
        features = ExtractedFeatures()
        
        # Extract property type
        features.property_type, features.property_type_confidence = self._extract_property_type(description_lower)
        
        # Extract amenities
        features.amenities, features.amenities_confidence = self._extract_amenities(description_lower)
        
        # Extract style
        features.style, features.style_confidence = self._extract_style(description_lower)
        
        # Extract rooms
        features.rooms, features.rooms_confidence = self._extract_rooms(description_lower)
        
        # Extract materials
        features.materials, features.materials_confidence = self._extract_materials(description_lower)
        
        logger.info(f"Extracted features: property_type={features.property_type}, "
                   f"amenities={len(features.amenities)}, style={features.style}")
        
        return features
    
    def _extract_property_type(self, text: str) -> Tuple[Optional[str], float]:
        """Extract property type with confidence score."""
        scores = {}
        text_len = len(text)
        
        for prop_type, keywords in self.property_types.items():
            score = 0
            for keyword in keywords:
                if keyword in text.lower():
                    # Score based on keyword length relative to text length
                    keyword_score = len(keyword) / text_len
                    # Bonus for exact matches vs partial matches
                    if keyword in text.lower().split():
                        keyword_score *= 1.5  # Exact word match gets bonus
                    score += keyword_score
            
            if score > 0:
                scores[prop_type] = min(score, 1.0)
        
        # Special handling for townhouse vs house - prefer explicit mentions
        if 'townhouse' in scores and 'house' in scores:
            # Check if townhouse was explicitly mentioned
            if 'townhouse' in text.lower() or 'townhome' in text.lower():
                if scores['townhouse'] >= scores['house'] * 0.7:  # Allow slightly lower confidence
                    return 'townhouse', scores['townhouse']
            # Otherwise default to house for ambiguous cases
            return 'house', scores['house']
        
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type, scores[best_type]
        
        return None, 0.0
    
    def _extract_amenities(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """Extract amenities with confidence scores."""
        found_amenities = []
        confidence_scores = {}
        
        for amenity, keywords in self.amenities.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # Score based on keyword length and exactness
                    score += len(keyword) / len(text) * 100
            
            if score > 0.1:  # Minimum threshold
                found_amenities.append(amenity)
                confidence_scores[amenity] = min(score, 1.0)
        
        return found_amenities, confidence_scores
    
    def _extract_style(self, text: str) -> Tuple[Optional[str], float]:
        """Extract architectural style with confidence score."""
        scores = {}
        
        for style, keywords in self.styles.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += len(keyword) / len(text) * 100
            if score > 0:
                scores[style] = min(score, 1.0)
        
        if scores:
            best_style = max(scores, key=scores.get)
            return best_style, scores[best_style]
        
        return None, 0.0
    
    def _extract_rooms(self, text: str) -> Tuple[Dict[str, int], Dict[str, float]]:
        """Extract room counts with confidence scores."""
        rooms = {}
        confidence_scores = {}
        
        for room_type, keywords in self.rooms.items():
            count = 0
            confidence = 0.0
            
            for keyword in keywords:
                # Look for numbers before room type (e.g., "3 bedroom", "2-bathroom")
                patterns = [
                    r'(\d+)\s*' + re.escape(keyword),  # "3 bedroom"
                    r'(\d+)-' + re.escape(keyword),  # "3-bedroom" 
                    re.escape(keyword) + r'\s*(\d+)',  # "bedroom 3"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        try:
                            count = max(int(m) for m in matches if m.isdigit())
                            confidence = min(len(keyword) / len(text) * 100, 1.0)
                            break
                        except (ValueError, IndexError):
                            continue
                    
                    if count > 0:
                        break
            
            if count > 0:
                rooms[room_type] = count
                confidence_scores[room_type] = confidence
        
        return rooms, confidence_scores
    
    def _extract_materials(self, text: str) -> Tuple[List[str], Dict[str, float]]:
        """Extract materials with confidence scores."""
        found_materials = []
        confidence_scores = {}
        
        for material, keywords in self.materials.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += len(keyword) / len(text) * 100
            
            if score > 0.1:  # Minimum threshold
                found_materials.append(material)
                confidence_scores[material] = min(score, 1.0)
        
        return found_materials, confidence_scores
    
    def to_dict(self, features: ExtractedFeatures) -> Dict[str, Any]:
        """Convert ExtractedFeatures to dictionary format."""
        return {
            'property_type': features.property_type,
            'property_type_confidence': features.property_type_confidence,
            'amenities': features.amenities,
            'amenities_confidence': features.amenities_confidence,
            'style': features.style,
            'style_confidence': features.style_confidence,
            'rooms': features.rooms,
            'rooms_confidence': features.rooms_confidence,
            'materials': features.materials,
            'materials_confidence': features.materials_confidence,
        }


# Global instance for convenience
_extractor = None

def get_extractor() -> PropertyFeatureExtractor:
    """Get or create the global feature extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = PropertyFeatureExtractor()
    return _extractor

def extract_features(description: str) -> Dict[str, Any]:
    """
    Convenience function to extract features from a description.
    
    Args:
        description: Natural language description from vision model
        
    Returns:
        Dictionary containing extracted features with confidence scores
    """
    extractor = get_extractor()
    features = extractor.extract_features(description)
    return extractor.to_dict(features)