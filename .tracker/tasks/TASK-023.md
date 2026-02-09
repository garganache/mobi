# TASK-023: Write unit tests for field suggestion algorithm

**Story:** STORY-004
**Status:** todo
**Priority:** high
**Estimated:** 2h

## Description

Test the field suggestion algorithm to verify it prioritizes fields correctly and returns appropriate suggestions based on property state.

## Test Cases

- Returns 2-3 fields maximum
- Prioritizes required fields first
- Filters irrelevant fields by property type
- Suggests verification for detected features
- Handles completely filled forms
- Handles empty forms
- Respects field dependencies

## Definition of Done

- [ ] Test file created for suggestion algorithm
- [ ] All prioritization rules tested
- [ ] Different property types tested
- [ ] Edge cases covered
- [ ] Algorithm logic documented in tests
