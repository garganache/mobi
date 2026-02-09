import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { listingStore, listingValues, aiSuggestions } from '../listingStore';

describe('State Management - Additional Test Coverage', () => {
  beforeEach(() => {
    listingStore.reset();
  });

  describe('State Initialization and Empty States', () => {
    it('state initializes empty by default', () => {
      const state = get(listingStore);
      expect(state).toEqual({});
    });

    it('getFieldValue returns null for non-existent fields in empty state', () => {
      const value = listingStore.getFieldValue('nonexistent');
      expect(value).toBeNull();
    });

    it('toJSON returns empty object for empty state', () => {
      const json = listingStore.toJSON();
      expect(json).toEqual({});
    });

    it('derived stores work correctly with empty state', () => {
      const values = get(listingValues);
      const suggestions = get(aiSuggestions);
      
      expect(values).toEqual({});
      expect(suggestions).toEqual({});
    });
  });

  describe('State Updates and Reactivity', () => {
    it('state updates trigger reactive updates', () => {
      let updateCount = 0;
      let latestValue: any = null;
      
      const unsubscribe = listingStore.subscribe((state) => {
        updateCount++;
        latestValue = state.testField?.value;
      });

      expect(updateCount).toBe(1); // Initial subscription
      expect(latestValue).toBeUndefined();

      listingStore.setFieldValue('testField', 'new value');
      expect(updateCount).toBe(2);
      expect(latestValue).toBe('new value');

      listingStore.setFieldValue('testField', 'updated value');
      expect(updateCount).toBe(3);
      expect(latestValue).toBe('updated value');

      unsubscribe();
    });

    it('multiple subscribers receive the same updates', () => {
      let count1 = 0;
      let count2 = 0;
      let value1: any = null;
      let value2: any = null;
      
      const unsub1 = listingStore.subscribe((state) => {
        count1++;
        value1 = state.testField?.value;
      });

      const unsub2 = listingStore.subscribe((state) => {
        count2++;
        value2 = state.testField?.value;
      });

      listingStore.setFieldValue('testField', 'shared value');
      
      expect(count1).toBeGreaterThan(1);
      expect(count2).toBeGreaterThan(1);
      expect(value1).toBe('shared value');
      expect(value2).toBe('shared value');

      unsub1();
      unsub2();
    });

    it('state updates are synchronous', () => {
      let valueBefore: any = null;
      let valueAfter: any = null;
      
      listingStore.setFieldValue('syncField', 'initial');
      
      valueBefore = listingStore.getFieldValue('syncField');
      listingStore.setFieldValue('syncField', 'updated');
      valueAfter = listingStore.getFieldValue('syncField');
      
      expect(valueBefore).toBe('initial');
      expect(valueAfter).toBe('updated');
    });
  });

  describe('Multiple Fields Independence', () => {
    it('multiple fields update completely independently', () => {
      // Set up multiple fields with different types
      listingStore.setFieldValue('field1', 'string value');
      listingStore.setFieldValue('field2', 42);
      listingStore.setFieldValue('field3', true);
      listingStore.setFieldValue('field4', null);
      
      // Update each field and verify others remain unchanged
      listingStore.setFieldValue('field1', 'updated string');
      
      expect(listingStore.getFieldValue('field1')).toBe('updated string');
      expect(listingStore.getFieldValue('field2')).toBe(42);
      expect(listingStore.getFieldValue('field3')).toBe(true);
      expect(listingStore.getFieldValue('field4')).toBeNull();
      
      // Update another field
      listingStore.setFieldValue('field3', false);
      
      expect(listingStore.getFieldValue('field1')).toBe('updated string');
      expect(listingStore.getFieldValue('field2')).toBe(42);
      expect(listingStore.getFieldValue('field3')).toBe(false);
      expect(listingStore.getFieldValue('field4')).toBeNull();
    });

    it('field updates do not interfere with each other\'s metadata', () => {
      listingStore.setFieldValue('userField', 'user value');
      listingStore.setAISuggestion('aiField', 'ai value');
      listingStore.initField('defaultField', 'default value');
      
      // Update user field
      listingStore.setFieldValue('userField', 'updated user');
      
      const state = get(listingStore);
      expect(state.userField.userModified).toBe(true);
      expect(state.userField.source).toBe('user');
      
      expect(state.aiField.userModified).toBe(false);
      expect(state.aiField.source).toBe('ai');
      
      expect(state.defaultField.userModified).toBe(false);
      expect(state.defaultField.source).toBe('default');
    });
  });

  describe('State Serialization and JSON', () => {
    it('state can be serialized to JSON with complex data types', () => {
      listingStore.setFieldValue('stringField', 'test string');
      listingStore.setFieldValue('numberField', 123.45);
      listingStore.setFieldValue('booleanField', true);
      listingStore.setFieldValue('nullField', null);
      listingStore.setFieldValue('zeroField', 0);
      listingStore.setFieldValue('emptyStringField', '');
      
      const json = listingStore.toJSON();
      
      expect(json).toEqual({
        stringField: 'test string',
        numberField: 123.45,
        booleanField: true,
        nullField: null,
        zeroField: 0,
        emptyStringField: '',
      });
      
      // Verify JSON is serializable
      expect(() => JSON.stringify(json)).not.toThrow();
    });

    it('JSON serialization excludes metadata correctly', () => {
      listingStore.setFieldValue('field1', 'value1');
      listingStore.setAISuggestion('field2', 'ai value');
      
      const json = listingStore.toJSON();
      
      expect(json).toEqual({
        field1: 'value1',
        field2: 'ai value', // AI value since user hasn't modified
      });
      
      // Verify no metadata in JSON
      expect(json).not.toHaveProperty('userModified');
      expect(json).not.toHaveProperty('source');
      expect(json).not.toHaveProperty('aiSuggested');
    });

    it('JSON round-trip preserves values but not metadata', () => {
      const originalState = {
        field1: { value: 'value1', userModified: true, source: 'user' as const },
        field2: { value: 'value2', userModified: false, source: 'ai' as const, aiSuggested: 'ai value' },
      };
      
      listingStore.loadState(originalState);
      
      const json = listingStore.toJSON();
      listingStore.reset();
      
      // Load from JSON (this would be a simplified state)
      Object.entries(json).forEach(([key, value]) => {
        listingStore.setFieldValue(key, value);
      });
      
      // Values are preserved but metadata is lost
      expect(listingStore.getFieldValue('field1')).toBe('value1');
      expect(listingStore.getFieldValue('field2')).toBe('value2');
    });
  });

  describe('State Reset Functionality', () => {
    it('state resets correctly with various field types', () => {
      // Set up complex state
      listingStore.setFieldValue('stringField', 'test');
      listingStore.setFieldValue('numberField', 42);
      listingStore.setFieldValue('booleanField', true);
      listingStore.setAISuggestion('aiField', 'ai value');
      listingStore.initField('defaultField', 'default');
      
      expect(Object.keys(get(listingStore)).length).toBeGreaterThan(0);
      
      // Reset
      listingStore.reset();
      
      const state = get(listingStore);
      expect(state).toEqual({});
      expect(Object.keys(state).length).toBe(0);
    });

    it('state reset allows new state to be set', () => {
      listingStore.setFieldValue('field1', 'value1');
      listingStore.reset();
      
      // Should be able to set new values after reset
      listingStore.setFieldValue('field2', 'value2');
      
      expect(listingStore.getFieldValue('field2')).toBe('value2');
      expect(listingStore.getFieldValue('field1')).toBeNull(); // Original field should be gone
    });

    it('multiple resets work correctly', () => {
      listingStore.setFieldValue('field', 'value');
      listingStore.reset();
      listingStore.reset(); // Second reset
      listingStore.reset(); // Third reset
      
      expect(get(listingStore)).toEqual({});
    });
  });

  describe('Nested Objects and Complex Structures', () => {
    it('handles nested objects in field values', () => {
      const nestedObject = {
        level1: {
          level2: {
            value: 'deep value'
          }
        }
      };
      
      listingStore.setFieldValue('nestedField', nestedObject);
      
      const retrieved = listingStore.getFieldValue('nestedField');
      expect(retrieved).toEqual(nestedObject);
      expect(retrieved.level1.level2.value).toBe('deep value');
    });

    it('handles arrays in field values', () => {
      const arrayValue = ['item1', 'item2', { nested: true }];
      
      listingStore.setFieldValue('arrayField', arrayValue);
      
      const retrieved = listingStore.getFieldValue('arrayField');
      expect(retrieved).toEqual(arrayValue);
      expect(retrieved.length).toBe(3);
    });

    it('handles complex nested structures in JSON serialization', () => {
      const complexValue = {
        string: 'test',
        number: 42,
        boolean: true,
        array: [1, 2, 3],
        nested: {
          deep: {
            value: 'deep'
          }
        },
        nullValue: null
      };
      
      listingStore.setFieldValue('complexField', complexValue);
      
      const json = listingStore.toJSON();
      expect(json.complexField).toEqual(complexValue);
      
      // Verify the complex structure is preserved
      expect(json.complexField.nested.deep.value).toBe('deep');
      expect(json.complexField.array).toEqual([1, 2, 3]);
    });

    it('nested objects maintain reference equality', () => {
      const originalObject = { nested: { value: 'test' } };
      listingStore.setFieldValue('nestedField', originalObject);
      
      const retrieved = listingStore.getFieldValue('nestedField');
      
      // Should be the same object (reference equality)
      expect(retrieved).toBe(originalObject);
    });
  });

  describe('Performance and Large Forms', () => {
    it('handles large number of fields efficiently', () => {
      const startTime = performance.now();
      
      // Create 1000 fields
      for (let i = 0; i < 1000; i++) {
        listingStore.setFieldValue(`field_${i}`, `value_${i}`);
      }
      
      const createTime = performance.now() - startTime;
      
      // Verify all fields were created
      const state = get(listingStore);
      expect(Object.keys(state).length).toBe(1000);
      
      // Verify random field
      expect(listingStore.getFieldValue('field_500')).toBe('value_500');
      
      // Creation should be reasonably fast (less than 1 second for 1000 fields)
      expect(createTime).toBeLessThan(1000);
    });

    it('rapid successive updates perform well', () => {
      const iterations = 100;
      const startTime = performance.now();
      
      // Rapid updates to the same field
      for (let i = 0; i < iterations; i++) {
        listingStore.setFieldValue('rapidField', `value_${i}`);
      }
      
      const updateTime = performance.now() - startTime;
      
      expect(listingStore.getFieldValue('rapidField')).toBe(`value_${iterations - 1}`);
      expect(updateTime).toBeLessThan(100); // Should be very fast
    });

    it('JSON serialization performance with many fields', () => {
      // Create many fields
      for (let i = 0; i < 500; i++) {
        listingStore.setFieldValue(`field_${i}`, `value_${i}`);
      }
      
      const startTime = performance.now();
      const json = listingStore.toJSON();
      const serializeTime = performance.now() - startTime;
      
      expect(Object.keys(json).length).toBe(500);
      expect(serializeTime).toBeLessThan(50); // Should be very fast
    });
  });

  describe('Edge Cases and Error Conditions', () => {
    it('handles undefined values gracefully', () => {
      listingStore.setFieldValue('undefinedField', undefined);
      
      const value = listingStore.getFieldValue('undefinedField');
      expect(value).toBeNull(); // Store converts undefined to null
    });

    it('handles special number values', () => {
      listingStore.setFieldValue('infinity', Infinity);
      listingStore.setFieldValue('negInfinity', -Infinity);
      listingStore.setFieldValue('nan', NaN);
      
      expect(listingStore.getFieldValue('infinity')).toBe(Infinity);
      expect(listingStore.getFieldValue('negInfinity')).toBe(-Infinity);
      expect(listingStore.getFieldValue('nan')).toBeNaN();
    });

    it('handles very long field IDs', () => {
      const longId = 'field_' + 'x'.repeat(1000);
      const value = 'test value';
      
      listingStore.setFieldValue(longId, value);
      
      expect(listingStore.getFieldValue(longId)).toBe(value);
    });

    it('handles field IDs with special characters', () => {
      const specialIds = [
        'field-with-dashes',
        'field_with_underscores', 
        'field.with.dots',
        'field:with:colons',
        'field/with/slashes',
        'field with spaces',
        'field@with@symbols',
        'field123with456numbers',
        'UPPERCASE_FIELD',
        'MixedCase_Field'
      ];
      
      specialIds.forEach((id, index) => {
        listingStore.setFieldValue(id, `value_${index}`);
      });
      
      specialIds.forEach((id, index) => {
        expect(listingStore.getFieldValue(id)).toBe(`value_${index}`);
      });
    });

    it('handles empty operations without errors', () => {
      expect(() => {
        listingStore.reset();
        listingStore.reset();
        listingStore.toJSON();
        listingStore.getFieldValue('');
      }).not.toThrow();
    });
  });

  describe('State Consistency Across Operations', () => {
    it('maintains consistency through complex operation sequences', () => {
      // Complex sequence of operations
      listingStore.initField('field1', 'default');
      listingStore.setAISuggestion('field1', 'ai value');
      listingStore.setFieldValue('field1', 'user value');
      listingStore.setAISuggestion('field1', 'new ai value');
      
      const state = get(listingStore);
      expect(state.field1.value).toBe('user value');
      expect(state.field1.aiSuggested).toBe('new ai value');
      expect(state.field1.userModified).toBe(true);
      expect(state.field1.source).toBe('user');
    });

    it('state remains consistent after loadState operations', () => {
      const complexState = {
        field1: { value: 'value1', userModified: true, source: 'user' as const },
        field2: { value: 42, userModified: false, source: 'ai' as const, aiSuggested: 45 },
        field3: { value: true, userModified: false, source: 'default' as const },
      };
      
      listingStore.loadState(complexState);
      
      // Verify loaded state
      expect(listingStore.getFieldValue('field1')).toBe('value1');
      expect(listingStore.getFieldValue('field2')).toBe(42);
      expect(listingStore.getFieldValue('field3')).toBe(true);
      
      // Verify metadata preservation
      const state = get(listingStore);
      expect(state.field1.userModified).toBe(true);
      expect(state.field2.aiSuggested).toBe(45);
      expect(state.field3.source).toBe('default');
    });
  });
});