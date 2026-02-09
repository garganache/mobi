# TASK-011: Implement field suggestion algorithm based on missing data

**Story:** STORY-004
**Status:** todo
**Priority:** high
**Estimated:** 3h

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

## Definition of Done

- [ ] Field suggestion function created
- [ ] Prioritization logic implemented
- [ ] Returns 2-3 fields maximum
- [ ] Considers property type in suggestions
- [ ] Handles edge cases (all fields filled, no detections)
- [ ] Algorithm tested with various scenarios
