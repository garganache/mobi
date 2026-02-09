# TASK-008: Implement basic orchestration logic for field prioritization

**Story:** STORY-003
**Status:** completed
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

- [x] Orchestration function created
- [x] Rule-based logic implemented for at least 2 property types
- [x] Field prioritization works (most important fields first)
- [x] Returns 2-3 fields maximum per step
- [x] Filters out irrelevant fields based on property type
- [x] Logic tested with different input scenarios

## Completion Notes

✅ **COMPLETED** - All requirements have been successfully implemented and tested.

The orchestration logic has been implemented in `/home/ubuntu/mobi/backend/app/orchestrator.py` with the following features:

- **FieldOrchestrator class** with `get_next_fields()` method that determines which fields to show next
- **Rule-based logic** for house, apartment, and condo property types with specific fields for each
- **Priority-based field ordering** using numerical priorities (lower = higher priority)
- **Maximum 3 fields per step** to avoid overwhelming users
- **Smart filtering** that only shows relevant fields based on property type
- **Comprehensive testing** with 12 unit tests and 11 integration tests - all passing

The implementation successfully handles the logic examples from the requirements:
- Missing `property_type` → asks for it first
- `property_type == "house"` → suggests lot_size, roof_age, garage, etc.
- `property_type == "apartment"` → suggests floor_number, elevator, building_age, etc.

All tests pass and the orchestration logic is ready for integration with the main application.
