"""
Field suggestion algorithm for the Mobi AI-guided listing system.

This module implements the intelligent field suggestion logic that analyzes
current form state, detected features, and property type to determine which
fields are most important to ask for next.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SuggestionCriteria:
    """Criteria for field suggestion prioritization."""
    field_id: str
    priority: int  # 1-10, where 1 is highest priority
    category: str  # 'required', 'high_value', 'detected', 'contextual'
    confidence: float = 1.0  # Confidence in the suggestion (0.0 - 1.0)
    reason: str = ""  # Human-readable reason for this suggestion


class FieldSuggestionAlgorithm:
    """
    Implements the field suggestion algorithm for progressive disclosure.
    
    This algorithm analyzes:
    1. Current form state (what's already filled)
    2. Detected features from images/text
    3. Property type and its specific requirements
    4. Field importance categories
    
    Returns the 2-3 most important missing fields to ask for next.
    """
    
    def __init__(self):
        self.max_suggestions = 3
        
        # Required fields by category (must be filled for a complete listing)
        self.required_fields = {
            'essential': ['property_type', 'address', 'price', 'bedrooms', 'bathrooms'],
            'property_specific': {
                'house': ['lot_size', 'stories'],
                'apartment': ['floor_number'],
                'condo': ['condo_fees'],
            }
        }
        
        # High-value fields that significantly impact listing quality
        self.high_value_fields = [
            'square_feet', 'description', 'has_parking', 'has_pool',
            'garage', 'building_age', 'amenities'
        ]
        
        # Fields that should be suggested when corresponding features are detected
        self.feature_field_mapping = {
            'pool': ['has_pool', 'pool_type'],
            'garage': ['has_parking', 'garage'],
            'balcony': ['balcony_type'],
            'fireplace': ['fireplace_type'],
            'garden': ['garden_type'],
            'elevator': ['elevator_type'],
            'gym': ['gym_type'],
            'security': ['security_system'],
            'air_conditioning': ['ac_type'],
            'hardwood_floors': ['flooring_type'],
            'granite_counters': ['countertop_material']
        }
        
        # Contextual field relationships
        self.contextual_relationships = {
            'has_pool': ['pool_type', 'pool_maintenance'],
            'has_parking': ['parking_type', 'parking_spaces'],
            'property_type': {  # Property type specific follow-ups
                'house': ['lot_size', 'stories', 'roof_age', 'garage'],
                'apartment': ['floor_number', 'elevator', 'pets_allowed'],
                'condo': ['condo_fees', 'amenities', 'building_age'],
            }
        }
    
    def suggest_fields(
        self, 
        current_data: Dict[str, Any], 
        detected_features: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Suggest the next 2-3 most important fields to ask for.
        
        Args:
            current_data: Current form state (field_id: value pairs)
            detected_features: Features detected from images/text analysis
            confidence_threshold: Minimum confidence for detected feature suggestions
            
        Returns:
            List of field suggestions (max 3) with configuration
        """
        detected_features = detected_features or {}
        
        # Get all missing fields
        missing_fields = self._get_missing_fields(current_data)
        
        if not missing_fields:
            logger.info("No missing fields to suggest")
            return []
        
        # Categorize and prioritize missing fields
        suggestions = self._prioritize_fields(
            missing_fields, 
            current_data, 
            detected_features,
            confidence_threshold
        )
        
        # Limit to max suggestions and convert to field configs
        final_suggestions = []
        for criteria in suggestions[:self.max_suggestions]:
            field_config = self._create_field_config(criteria.field_id, current_data)
            if field_config:
                final_suggestions.append(field_config)
        
        logger.info(f"Generated {len(final_suggestions)} field suggestions")
        return final_suggestions
    
    def _get_missing_fields(self, current_data: Dict[str, Any]) -> List[str]:
        """Get all fields that haven't been filled yet."""
        all_possible_fields = self._get_all_possible_fields(current_data)
        filled_fields = set(current_data.keys())
        
        missing_fields = [field for field in all_possible_fields if field not in filled_fields]
        return missing_fields
    
    def _get_all_possible_fields(self, current_data: Dict[str, Any]) -> List[str]:
        """Get all possible fields based on current form state."""
        fields = set()
        
        # Essential fields (including property_type)
        fields.update(self.required_fields['essential'])
        
        # Property-specific required fields
        property_type = current_data.get('property_type')
        if property_type and property_type in self.required_fields['property_specific']:
            fields.update(self.required_fields['property_specific'][property_type])
        
        # High-value fields
        fields.update(self.high_value_fields)
        
        # Feature-specific fields
        for feature_fields in self.feature_field_mapping.values():
            fields.update(feature_fields)
        
        # Contextual relationship fields
        for relationship_fields in self.contextual_relationships.values():
            if isinstance(relationship_fields, list):
                fields.update(relationship_fields)
            elif isinstance(relationship_fields, dict):
                for prop_fields in relationship_fields.values():
                    if isinstance(prop_fields, list):
                        fields.update(prop_fields)
        
        # Always include property_type if not present (it's handled specially)
        if 'property_type' not in current_data:
            fields.add('property_type')
        
        return list(fields)
    
    def _prioritize_fields(
        self,
        missing_fields: List[str],
        current_data: Dict[str, Any],
        detected_features: Dict[str, Any],
        confidence_threshold: float
    ) -> List[SuggestionCriteria]:
        """Prioritize missing fields based on multiple criteria."""
        criteria_list = []
        
        for field_id in missing_fields:
            # Check if field relates to detected features (highest priority if high confidence)
            feature_priority = self._get_feature_priority(field_id, detected_features, confidence_threshold)
            if feature_priority and feature_priority['confidence'] > 0.7:  # High confidence detected features
                criteria_list.append(SuggestionCriteria(
                    field_id=field_id,
                    priority=1,  # Highest priority for high-confidence detected features
                    category='detected',
                    confidence=feature_priority['confidence'],
                    reason=f"Detected {feature_priority['feature']} in image/text"
                ))
                continue
            
            # Check if field is required
            if self._is_required_field(field_id, current_data):
                criteria_list.append(SuggestionCriteria(
                    field_id=field_id,
                    priority=2,  # Second priority for required fields
                    category='required',
                    reason='Required field for complete listing'
                ))
                continue
            
            # Check if field relates to detected features (lower confidence)
            if feature_priority:
                criteria_list.append(SuggestionCriteria(
                    field_id=field_id,
                    priority=3,  # Third priority for lower-confidence detected features
                    category='detected',
                    confidence=feature_priority['confidence'],
                    reason=f"Detected {feature_priority['feature']} in image/text"
                ))
                continue
            
            # Check if field is high-value
            if field_id in self.high_value_fields:
                priority = self._get_high_value_priority(field_id, current_data)
                criteria_list.append(SuggestionCriteria(
                    field_id=field_id,
                    priority=priority + 3,  # Adjusted priority
                    category='high_value',
                    reason='High-value field that improves listing quality'
                ))
                continue
            
            # Check contextual relationships
            contextual_priority = self._get_contextual_priority(field_id, current_data)
            if contextual_priority:
                criteria_list.append(SuggestionCriteria(
                    field_id=field_id,
                    priority=contextual_priority['priority'] + 5,  # Adjusted priority
                    category='contextual',
                    reason=contextual_priority['reason']
                ))
        
        # Sort by priority (lower number = higher priority)
        criteria_list.sort(key=lambda x: (x.priority, -x.confidence))
        
        return criteria_list
    
    def _is_required_field(self, field_id: str, current_data: Dict[str, Any]) -> bool:
        """Check if a field is required."""
        # Essential required fields
        if field_id in self.required_fields['essential']:
            return True
        
        # Property-specific required fields
        property_type = current_data.get('property_type')
        if (property_type and 
            property_type in self.required_fields['property_specific'] and
            field_id in self.required_fields['property_specific'][property_type]):
            return True
        
        return False
    
    def _get_feature_priority(
        self, 
        field_id: str, 
        detected_features: Dict[str, Any], 
        confidence_threshold: float
    ) -> Optional[Dict[str, Any]]:
        """Get priority for fields related to detected features."""
        amenities = detected_features.get('amenities', [])
        amenities_conf = detected_features.get('amenities_confidence', {})
        
        for feature, related_fields in self.feature_field_mapping.items():
            if field_id in related_fields:
                # Check if feature was detected with sufficient confidence
                if feature in amenities:
                    confidence = amenities_conf.get(feature, 0.0)
                    if confidence >= confidence_threshold:
                        return {
                            'priority': 1,  # Highest priority for detected features
                            'confidence': confidence,
                            'feature': feature
                        }
        
        return None
    
    def _get_high_value_priority(self, field_id: str, current_data: Dict[str, Any]) -> int:
        """Get priority for high-value fields based on current state."""
        # Price and square feet are always high priority
        if field_id in ['price', 'square_feet']:
            return 3
        
        # Description becomes more important as other fields are filled
        if field_id == 'description':
            filled_count = len(current_data)
            if filled_count >= 5:
                return 4
            elif filled_count >= 3:
                return 6
            else:
                return 8
        
        # Default priority for other high-value fields
        return 5
    
    def _get_contextual_priority(self, field_id: str, current_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get priority based on contextual relationships."""
        property_type = current_data.get('property_type')
        
        # Property type specific follow-ups
        if property_type and property_type in self.contextual_relationships.get('property_type', {}):
            prop_fields = self.contextual_relationships['property_type'][property_type]
            if field_id in prop_fields:
                priority = 2 + prop_fields.index(field_id)  # Earlier fields get higher priority
                return {
                    'priority': priority,
                    'reason': f'Important for {property_type} properties'
                }
        
        # Conditional fields based on current data
        if field_id in self.contextual_relationships.get('has_pool', []) and current_data.get('has_pool'):
            return {'priority': 2, 'reason': 'Pool detected, need details'}
        
        if field_id in self.contextual_relationships.get('has_parking', []) and current_data.get('has_parking'):
            return {'priority': 3, 'reason': 'Parking confirmed, need details'}
        
        return None
    
    def _create_field_config(self, field_id: str, current_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create field configuration based on field ID and current state."""
        # Get field definition from orchestrator or create custom one
        from app.orchestrator import COMMON_FIELDS, PROPERTY_TYPE_FIELDS
        
        # Special handling for property_type field
        if field_id == 'property_type':
            return {
                'id': 'property_type',
                'component_type': 'select',
                'label': 'Property Type',
                'placeholder': 'Select property type',
                'options': [
                    {'value': 'house', 'label': 'House'},
                    {'value': 'apartment', 'label': 'Apartment'},
                    {'value': 'condo', 'label': 'Condo'},
                    {'value': 'townhouse', 'label': 'Townhouse'},
                ],
                'required': True,
            }
        
        # Check common fields
        for field in COMMON_FIELDS:
            if field['id'] == field_id:
                return field.copy()
        
        # Check property-specific fields
        property_type = current_data.get('property_type')
        if property_type and property_type in PROPERTY_TYPE_FIELDS:
            for field in PROPERTY_TYPE_FIELDS[property_type]:
                if field['id'] == field_id:
                    return field.copy()
        
        # Create custom field configs for feature-specific fields
        custom_configs = {
            'pool_type': {
                'id': 'pool_type',
                'component_type': 'select',
                'label': 'Pool Type',
                'options': [
                    {'value': 'chlorine', 'label': 'Chlorine'},
                    {'value': 'salt', 'label': 'Salt Water'},
                    {'value': 'natural', 'label': 'Natural/Organic'},
                ],
                'required': False,
            },
            'has_pool': {
                'id': 'has_pool',
                'component_type': 'toggle',
                'label': 'Has Pool',
                'required': False,
            },
            'garage': {
                'id': 'garage',
                'component_type': 'select',
                'label': 'Garage Type',
                'options': [
                    {'value': 'none', 'label': 'No Garage'},
                    {'value': 'attached', 'label': 'Attached'},
                    {'value': 'detached', 'label': 'Detached'},
                    {'value': 'carport', 'label': 'Carport'},
                ],
                'required': False,
            },
        }
        
        return custom_configs.get(field_id)


# Global instance for convenience
_suggester = None

def get_field_suggester() -> FieldSuggestionAlgorithm:
    """Get or create the global field suggestion algorithm instance."""
    global _suggester
    if _suggester is None:
        _suggester = FieldSuggestionAlgorithm()
    return _suggester

def suggest_fields(
    current_data: Dict[str, Any], 
    detected_features: Optional[Dict[str, Any]] = None,
    confidence_threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Convenience function to suggest fields.
    
    Args:
        current_data: Current form state
        detected_features: Features detected from images/text
        confidence_threshold: Minimum confidence for detected features
        
    Returns:
        List of field suggestions
    """
    suggester = get_field_suggester()
    return suggester.suggest_fields(current_data, detected_features, confidence_threshold)