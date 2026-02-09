# TASK-005: Set up reactive state management for listing data

**Story:** STORY-002
**Status:** todo
**Priority:** high
**Estimated:** 2h

## Description

Create a reactive state management system to hold the listing form data. This state should update as users fill in fields and should be easily serializable to send to the backend.

## Technical Requirements

- Use Svelte stores or reactive object to hold form state
- State structure: `{ field_id: value }` pairs
- Bidirectional binding between components and state
- State should be serializable to JSON
- Consider adding a "shadow state" for AI-detected values vs user-entered values

## Definition of Done

- [ ] State management system created (store or reactive object)
- [ ] Form data updates when field values change
- [ ] State can be serialized to JSON
- [ ] State can be logged/inspected for debugging
- [ ] Clear separation between user input and AI suggestions (optional)
- [ ] State persists across component re-renders
