# TASK-016: Write unit tests for input components (TextInput, SelectInput, NumberInput)

**Story:** STORY-002
**Status:** todo
**Priority:** medium
**Estimated:** 3h

## Description

Write comprehensive unit tests for each input component using Vitest and Svelte Testing Library. Ensure components render correctly, handle user interactions, and emit proper events.

## Test Coverage

For each component (TextInput, SelectInput, NumberInput):

- Renders with correct label
- Displays initial value
- Updates value on user input
- Emits change events
- Handles disabled state
- Shows validation errors (if implemented)
- Applies correct ARIA attributes

## Definition of Done

- [ ] Test files created for each component
- [ ] All test cases passing
- [ ] Code coverage >80% for component logic
- [ ] Tests run in CI pipeline
- [ ] Edge cases tested (empty values, special characters)
