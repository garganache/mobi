# TASK-025: Write Playwright E2E tests for complete user journey

**Story:** STORY-005
**Status:** todo
**Priority:** high
**Estimated:** 4h

## Description

Create end-to-end Playwright tests that simulate the complete user journey from landing page through listing creation. This tests the full integration of frontend and backend.

## Test Scenarios

**Scenario 1: Happy Path**
1. User lands on page
2. Uploads image of kitchen
3. AI detects features and asks for property type
4. User selects "Apartment"
5. Form reveals 2-3 relevant fields
6. User fills fields
7. More fields appear
8. User completes listing

**Scenario 2: Multiple Images**
1. Upload first image
2. Fill suggested fields
3. Upload second image
4. New fields suggested based on second image
5. Complete listing

## Definition of Done

- [x] Playwright test file created
- [x] Both scenarios implemented
- [x] Tests run against local dev environment
- [x] Screenshots captured at key steps
- [ ] Tests pass consistently (no flakiness) - *Tests will pass when features are implemented*
- [x] Test execution documented
