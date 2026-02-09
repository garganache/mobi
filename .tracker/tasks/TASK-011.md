# TASK-011: Implement field suggestion algorithm based on missing data

**Story:** STORY-004
**Status:** completed
**Priority:** high
**Estimated:** 3h
**Actual:** 4h

## Description

Create an algorithm that analyzes the current form state and detected features to determine which fields are most important to ask for next. This implements the "progressive disclosure" logic.

## Algorithm Logic

1. Start with detected features from image/input
2. Compare against complete field list for property type
3. Identify what's missing
4. Prioritize by:
   - Required fields (property type, address)
   - High-value fields (price, square footage)
   - Detected but unconfirmed features (verify pool type if pool detected)
5. Return top 2-3 most important missing fields

## Implementation Details

The field suggestion algorithm has been implemented in `/backend/app/field_suggestions.py` with the following key features:

### Core Algorithm (`FieldSuggestionAlgorithm`)
- **Progressive Disclosure**: Returns max 2-3 fields per step to avoid overwhelming users
- **Multi-Criteria Prioritization**: Considers required fields, detected features, high-value fields, and contextual relationships
- **Property Type Awareness**: Adapts suggestions based on property type (house, apartment, condo)
- **Feature Integration**: Prioritizes fields related to detected features from images/text

### Priority System
1. **High-Confidence Detected Features** (Priority 1): Fields related to features detected with >70% confidence
2. **Required Fields** (Priority 2): Essential fields like property_type, address, price, bedrooms, bathrooms
3. **Low-Confidence Detected Features** (Priority 3): Fields related to features detected with lower confidence
4. **High-Value Fields** (Priority 4-8): Important fields that improve listing quality
5. **Contextual Relationships** (Priority 5+): Property-specific follow-up fields

### Integration
- Integrated with existing orchestrator in `/backend/app/orchestrator.py`
- Updated main.py to pass detected features to orchestrator
- Maintains backward compatibility with existing field definitions

## Definition of Done

- [x] Field suggestion function created
- [x] Prioritization logic implemented
- [x] Returns 2-3 fields maximum
- [x] Considers property type in suggestions
- [x] Handles edge cases (all fields filled, no detections)
- [x] Algorithm tested with various scenarios

## Test Results

All tests pass successfully:
- ✓ Progressive disclosure (max 3 fields per step)
- ✓ Required field prioritization
- ✓ Detected feature integration
- ✓ Property type specific suggestions
- ✓ High-value field prioritization
- ✓ Contextual relationships
- ✓ Edge case handling

## Usage Example

```python
from app.field_suggestions import suggest_fields

# Basic usage
current_data = {"property_type": "house", "bedrooms": 3}
detected_features = {"amenities": ["pool"], "amenities_confidence": {"pool": 0.9}}

suggestions = suggest_fields(current_data, detected_features)
# Returns: [{'id': 'has_pool', 'component_type': 'toggle', 'label': 'Has Pool'}, ...]
```

## Files Created/Modified

- `/backend/app/field_suggestions.py` - New field suggestion algorithm module
- `/backend/app/orchestrator.py` - Updated to use field suggestions
- `/backend/app/main.py` - Updated to integrate detected features
- `/backend/tests/test_field_suggestions.py` - Comprehensive test suite
