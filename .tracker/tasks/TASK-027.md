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

- [ ] Playwright test file created
- [ ] Progressive reveal verified
- [ ] Animation timing verified (using Playwright waits)
- [ ] Accessibility of new fields tested
- [ ] Tests handle timing/async correctly
