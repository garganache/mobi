# TASK-002: Create component registry mapping field types to Svelte components

**Story:** STORY-002
**Status:** done
**Priority:** high
**Estimated:** 1h

## Description

Create a component registry system that maps field type strings (e.g., 'text', 'select', 'toggle') to actual Svelte component imports. This registry will be used by the dynamic renderer to determine which component to instantiate based on the UI schema received from the backend.

## Technical Details

- Create a `componentMap` object/file in the Svelte app
- Map at least these types: 'text', 'select', 'number', 'toggle'
- Ensure the registry is easily extensible for future field types
- Consider using TypeScript for type safety

## Definition of Done

- [x] Component registry file created (e.g., `lib/components/fields/registry.ts`)
- [x] At least 4 field types mapped
- [x] Registry is importable and usable in parent components
- [x] Documentation added explaining how to add new field types
