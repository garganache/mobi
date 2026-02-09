# TASK-019: Write unit tests for /api/analyze-step endpoint

**Story:** STORY-003
**Status:** todo
**Priority:** high
**Estimated:** 2h

## Description

Write comprehensive tests for the FastAPI endpoint using pytest. Verify request handling, response format, and error cases.

## Test Cases

- Endpoint returns 200 for valid request
- Response matches UI Manifest schema
- Handles missing current_data
- Handles missing new_input
- Validates input types
- Returns proper error messages for invalid input
- CORS headers present (if configured)

## Definition of Done

- [ ] Test file created (test_analyze_step.py)
- [ ] All test cases passing
- [ ] Uses pytest fixtures for common data
- [ ] Tests both success and error paths
- [ ] Test coverage >90% for endpoint code
