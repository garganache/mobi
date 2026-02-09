# TASK-003: Build basic input components (TextInput, SelectInput, NumberInput)

**Story:** STORY-002
**Status:** done
**Priority:** high
**Estimated:** 3h

## Description

Create reusable Svelte input components that can accept dynamic props from the UI schema. Each component should handle its own validation, styling, and two-way data binding.

## Components to Build

1. **TextInput.svelte** - Single-line text input
2. **SelectInput.svelte** - Dropdown with options
3. **NumberInput.svelte** - Numeric input with optional min/max
4. **ToggleInput.svelte** (bonus) - Boolean on/off switch

## Technical Requirements

- Accept props: `id`, `label`, `placeholder`, `value`, `options` (for select)
- Use `bind:value` for two-way binding
- Include accessible labels and ARIA attributes
- Consistent styling across all components
- Error state support (for future validation)

## Definition of Done

- [x] All 3 components created (4 if toggle included)
- [x] Components accept required props
- [x] Two-way binding works correctly
- [x] Components are styled consistently
- [x] Accessibility attributes present (labels, aria-labels)
- [x] Components tested manually in isolation
