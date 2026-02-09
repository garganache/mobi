# TASK-027: Write Playwright tests for progressive field reveal

**Story:** STORY-005
**Status:** todo
**Priority:** medium
**Estimated:** 2h

## Description

Test the progressive disclosure behavior using Playwright to verify that fields appear dynamically based on user interactions and AI responses.

## Test Cases

- Initial state shows minimal fields
- After upload, new fields appear
- Field count increases progressively (not all at once)
- Animations run smoothly
- Fields are accessible after reveal
- Form scrolls to new fields if needed
- Previously filled fields remain visible

## Definition of Done

- [x] Playwright test file created
- [x] Progressive reveal verified
- [x] Animation timing verified (using Playwright waits)
- [x] Accessibility of new fields tested
- [x] Tests handle timing/async correctly
