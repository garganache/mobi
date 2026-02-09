# STORY-002: Dynamic Form Infrastructure (Svelte)

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-09

## Description

Build the foundational dynamic form system in Svelte that can render UI components based on JSON schema received from the backend. This system will serve as the canvas where AI-driven fields appear progressively as the user provides more information about their property listing.

The key concept is to move away from hard-coded forms toward a component registry approach where the backend dictates which fields to show.

## Key Requirements

- Component registry that maps field types (text, select, toggle) to Svelte components
- Dynamic component rendering using `<svelte:component>`
- Reactive state management for listing data
- Support for binding values bidirectionally between components and state
- Visual feedback (animations) when new fields are added

## Acceptance Criteria

- [ ] Component registry created with at least 3 field types mapped
- [ ] Reusable field components (TextInput, SelectInput, ToggleInput) implemented
- [ ] Dynamic rendering works: JSON schema → rendered form
- [ ] State updates correctly when user modifies field values
- [ ] New fields animate in smoothly (fly/fade transitions)
- [ ] Form state can be serialized and sent to backend

## Tasks

- TASK-002: Create component registry mapping field types to Svelte components
- TASK-003: Build basic input components (TextInput, SelectInput, NumberInput)
- TASK-004: Implement dynamic component rendering with svelte:component
- TASK-005: Set up reactive state management for listing data
- TASK-016: Write unit tests for input components (TextInput, SelectInput, NumberInput)
- TASK-017: Write unit tests for component registry and dynamic rendering
- TASK-018: Write unit tests for state management

## Notes

This story focuses purely on the Svelte infrastructure. It should work with mock JSON schemas before backend integration.
