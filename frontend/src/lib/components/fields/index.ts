/**
 * Field Components Index
 * 
 * Central export point for all field components and the component registry.
 */

export { default as TextInput } from './TextInput.svelte';
export { default as SelectInput } from './SelectInput.svelte';
export { default as NumberInput } from './NumberInput.svelte';
export { default as ToggleInput } from './ToggleInput.svelte';

export { componentMap, getComponent, hasComponent, getRegisteredTypes } from './registry';
export type { FieldType } from './registry';
