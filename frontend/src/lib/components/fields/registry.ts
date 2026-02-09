/**
 * Component Registry
 * 
 * Maps field type strings to their corresponding Svelte component imports.
 * This registry is used by the dynamic form renderer to determine which
 * component to instantiate based on the UI schema received from the backend.
 * 
 * ## Adding New Field Types
 * 
 * 1. Create a new component in `src/lib/components/fields/`
 * 2. Import the component at the top of this file
 * 3. Add a new entry to the `componentMap` object with the field type as key
 * 
 * Example:
 * ```typescript
 * import DateInput from './DateInput.svelte';
 * 
 * export const componentMap = {
 *   // ... existing entries
 *   'date': DateInput,
 * };
 * ```
 */

import TextInput from './TextInput.svelte';
import SelectInput from './SelectInput.svelte';
import NumberInput from './NumberInput.svelte';
import ToggleInput from './ToggleInput.svelte';
import type { ComponentType, SvelteComponent } from 'svelte';

/**
 * Type definition for field types supported by the registry
 */
export type FieldType = 'text' | 'select' | 'number' | 'toggle';

/**
 * Component map that associates field types with their Svelte components
 */
export const componentMap: Record<FieldType, ComponentType<SvelteComponent>> = {
  text: TextInput,
  select: SelectInput,
  number: NumberInput,
  toggle: ToggleInput,
};

/**
 * Get a component for a given field type
 * @param fieldType - The type of field to get a component for
 * @returns The Svelte component for the field type, or undefined if not found
 */
export function getComponent(fieldType: string): ComponentType<SvelteComponent> | undefined {
  return componentMap[fieldType as FieldType];
}

/**
 * Check if a field type is registered
 * @param fieldType - The type of field to check
 * @returns True if the field type has a registered component
 */
export function hasComponent(fieldType: string): boolean {
  return fieldType in componentMap;
}

/**
 * Get all registered field types
 * @returns Array of registered field type strings
 */
export function getRegisteredTypes(): FieldType[] {
  return Object.keys(componentMap) as FieldType[];
}
