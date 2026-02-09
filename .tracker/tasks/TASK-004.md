# TASK-004: Implement dynamic component rendering with svelte:component

**Story:** STORY-002
**Status:** done
**Priority:** high
**Estimated:** 2h

## Description

Build the dynamic rendering logic that takes a UI schema array from the backend and renders the appropriate components using Svelte's `<svelte:component>` directive. This is the core of the adaptive UI system.

## Technical Details

- Use `{#each schema as field}` to iterate over fields
- Use `<svelte:component this={componentMap[field.component_type]} {...field} />`
- Spread operator to pass all field properties as props
- Handle missing/unknown component types gracefully

## Definition of Done

- [x] Dynamic rendering implemented in main form component
- [x] Schema array properly iterated
- [x] Component type lookup works via registry
- [x] Props spread correctly to child components
- [x] Unknown component types show helpful error/fallback
- [x] Tested with mock schema data
