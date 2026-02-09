# TASK-017: Write unit tests for component registry and dynamic rendering

**Story:** STORY-002
**Status:** todo
**Priority:** medium
**Estimated:** 2h

## Description

Test the component registry and dynamic rendering logic to ensure field types are correctly mapped to components and that unknown types are handled gracefully.

## Test Cases

- Registry returns correct component for valid type
- Registry handles unknown types (error or fallback)
- Dynamic rendering creates correct number of components
- Props are spread correctly to child components
- Component updates when schema changes
- Empty schema renders nothing

## Definition of Done

- [ ] Test file created for registry/dynamic rendering
- [ ] All test cases passing
- [ ] Tests verify component instantiation
- [ ] Tests verify prop passing
- [ ] Edge cases covered (null schema, empty array)
