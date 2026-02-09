# TASK-008: Implement basic orchestration logic for field prioritization

**Story:** STORY-003
**Status:** todo
**Priority:** high
**Estimated:** 3h

## Description

Implement the logic that determines which fields to show next based on the current form state. Start with simple rule-based logic before integrating AI. This is the "brain" that decides what questions to ask.

## Logic Examples

- If `property_type` is missing → ask for it first
- If `property_type == "house"` → suggest fields: lot_size, roof_age, garage
- If `property_type == "apartment"` → suggest fields: floor_number, elevator, building_age
- Limit to 2-3 fields at a time to avoid overwhelming user

## Definition of Done

- [ ] Orchestration function created
- [ ] Rule-based logic implemented for at least 2 property types
- [ ] Field prioritization works (most important fields first)
- [ ] Returns 2-3 fields maximum per step
- [ ] Filters out irrelevant fields based on property type
- [ ] Logic tested with different input scenarios
