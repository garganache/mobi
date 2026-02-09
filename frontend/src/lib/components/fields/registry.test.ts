import { describe, it, expect } from 'vitest';
import { getComponent, hasComponent, getRegisteredTypes, componentMap } from './registry';
import TextInput from './TextInput.svelte';
import SelectInput from './SelectInput.svelte';
import NumberInput from './NumberInput.svelte';
import ToggleInput from './ToggleInput.svelte';

describe('Component Registry', () => {
  describe('getComponent', () => {
    it('returns the correct component for "text" type', () => {
      const component = getComponent('text');
      expect(component).toBe(TextInput);
    });

    it('returns the correct component for "select" type', () => {
      const component = getComponent('select');
      expect(component).toBe(SelectInput);
    });

    it('returns the correct component for "number" type', () => {
      const component = getComponent('number');
      expect(component).toBe(NumberInput);
    });

    it('returns the correct component for "toggle" type', () => {
      const component = getComponent('toggle');
      expect(component).toBe(ToggleInput);
    });

    it('returns undefined for unknown field type', () => {
      const component = getComponent('unknown-type');
      expect(component).toBeUndefined();
    });

    it('returns undefined for empty string', () => {
      const component = getComponent('');
      expect(component).toBeUndefined();
    });

    it('returns undefined for null-like values', () => {
      expect(getComponent('null')).toBeUndefined();
      expect(getComponent('undefined')).toBeUndefined();
    });

    it('is case-sensitive (returns undefined for uppercase)', () => {
      const component = getComponent('TEXT');
      expect(component).toBeUndefined();
    });
  });

  describe('hasComponent', () => {
    it('returns true for registered "text" type', () => {
      expect(hasComponent('text')).toBe(true);
    });

    it('returns true for registered "select" type', () => {
      expect(hasComponent('select')).toBe(true);
    });

    it('returns true for registered "number" type', () => {
      expect(hasComponent('number')).toBe(true);
    });

    it('returns true for registered "toggle" type', () => {
      expect(hasComponent('toggle')).toBe(true);
    });

    it('returns false for unknown field type', () => {
      expect(hasComponent('date')).toBe(false);
    });

    it('returns false for empty string', () => {
      expect(hasComponent('')).toBe(false);
    });

    it('returns false for non-existent types', () => {
      expect(hasComponent('random-type')).toBe(false);
      expect(hasComponent('email')).toBe(false);
      expect(hasComponent('password')).toBe(false);
    });

    it('is case-sensitive', () => {
      expect(hasComponent('TEXT')).toBe(false);
      expect(hasComponent('Select')).toBe(false);
    });
  });

  describe('getRegisteredTypes', () => {
    it('returns an array of all registered field types', () => {
      const types = getRegisteredTypes();
      expect(types).toEqual(['text', 'select', 'number', 'toggle']);
    });

    it('returns an array with the correct length', () => {
      const types = getRegisteredTypes();
      expect(types).toHaveLength(4);
    });

    it('returns all types that exist in componentMap', () => {
      const types = getRegisteredTypes();
      const mapKeys = Object.keys(componentMap);
      expect(types).toEqual(mapKeys);
    });

    it('returns types that all have corresponding components', () => {
      const types = getRegisteredTypes();
      types.forEach(type => {
        expect(hasComponent(type)).toBe(true);
        expect(getComponent(type)).toBeDefined();
      });
    });
  });

  describe('componentMap', () => {
    it('contains all expected field types', () => {
      expect(componentMap).toHaveProperty('text');
      expect(componentMap).toHaveProperty('select');
      expect(componentMap).toHaveProperty('number');
      expect(componentMap).toHaveProperty('toggle');
    });

    it('maps each type to a defined component', () => {
      Object.values(componentMap).forEach(component => {
        expect(component).toBeDefined();
      });
    });

    it('has exactly 4 registered components', () => {
      expect(Object.keys(componentMap)).toHaveLength(4);
    });
  });
});
