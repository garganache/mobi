# TASK-020: Write integration tests for UI manifest generation

**Story:** STORY-003
**Status:** done
**Priority:** medium
**Estimated:** 2h

## Description

Test the UI manifest generation logic to ensure it creates valid schemas based on different input scenarios and property types.

## Test Cases

- Generates schema for house property type
- Generates schema for apartment property type
- Limits fields to 2-3 per response
- Includes appropriate AI messages
- extracted_data matches detected features
- Schema adapts based on current_data state

## Definition of Done

- [x] Integration test file created
- [x] Tests cover multiple property types
- [x] Schema validation tested
- [x] Field prioritization verified
- [x] AI message generation tested
