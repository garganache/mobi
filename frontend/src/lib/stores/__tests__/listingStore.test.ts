import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { listingStore, listingValues, aiSuggestions } from '../listingStore';
import type { ListingState, FieldValue } from '../listingStore';

describe('listingStore', () => {
  // Reset store before each test to ensure isolation
  beforeEach(() => {
    listingStore.reset();
  });

  describe('setFieldValue', () => {
    it('sets a field value from user input', () => {
      listingStore.setFieldValue('title', 'Beautiful House');
      
      const state = get(listingStore);
      expect(state.title).toEqual({
        value: 'Beautiful House',
        userModified: true,
        source: 'user',
        aiSuggested: undefined,
      });
    });

    it('marks field as user modified', () => {
      listingStore.setFieldValue('price', 500000);
      
      const state = get(listingStore);
      expect(state.price.userModified).toBe(true);
      expect(state.price.source).toBe('user');
    });

    it('updates existing field value', () => {
      listingStore.setFieldValue('bedrooms', 3);
      listingStore.setFieldValue('bedrooms', 4);
      
      const state = get(listingStore);
      expect(state.bedrooms.value).toBe(4);
      expect(state.bedrooms.userModified).toBe(true);
    });

    it('preserves AI suggestion when updating user value', () => {
      listingStore.setAISuggestion('description', 'AI generated text');
      listingStore.setFieldValue('description', 'User entered text');
      
      const state = get(listingStore);
      expect(state.description.value).toBe('User entered text');
      expect(state.description.aiSuggested).toBe('AI generated text');
      expect(state.description.userModified).toBe(true);
    });

    it('handles null values', () => {
      listingStore.setFieldValue('garage', null);
      
      const state = get(listingStore);
      expect(state.garage.value).toBeNull();
    });

    it('handles boolean values', () => {
      listingStore.setFieldValue('furnished', true);
      
      const state = get(listingStore);
      expect(state.furnished.value).toBe(true);
      expect(typeof state.furnished.value).toBe('boolean');
    });

    it('handles string values', () => {
      listingStore.setFieldValue('city', 'New York');
      
      const state = get(listingStore);
      expect(state.city.value).toBe('New York');
    });

    it('handles number values', () => {
      listingStore.setFieldValue('squareFeet', 2000);
      
      const state = get(listingStore);
      expect(state.squareFeet.value).toBe(2000);
    });

    it('handles empty string values', () => {
      listingStore.setFieldValue('notes', '');
      
      const state = get(listingStore);
      expect(state.notes.value).toBe('');
    });

    it('handles zero as a valid number', () => {
      listingStore.setFieldValue('discount', 0);
      
      const state = get(listingStore);
      expect(state.discount.value).toBe(0);
    });

    it('can update multiple fields independently', () => {
      listingStore.setFieldValue('title', 'House A');
      listingStore.setFieldValue('price', 300000);
      listingStore.setFieldValue('bedrooms', 3);
      
      const state = get(listingStore);
      expect(state.title.value).toBe('House A');
      expect(state.price.value).toBe(300000);
      expect(state.bedrooms.value).toBe(3);
    });
  });

  describe('setAISuggestion', () => {
    it('sets AI suggestion for new field', () => {
      listingStore.setAISuggestion('description', 'AI suggested description');
      
      const state = get(listingStore);
      expect(state.description).toEqual({
        value: 'AI suggested description',
        aiSuggested: 'AI suggested description',
        userModified: false,
        source: 'ai',
      });
    });

    it('uses AI suggestion as value when field is not user-modified', () => {
      listingStore.setAISuggestion('title', 'AI Title');
      
      const state = get(listingStore);
      expect(state.title.value).toBe('AI Title');
      expect(state.title.source).toBe('ai');
    });

    it('does not overwrite user value with AI suggestion', () => {
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title');
      
      const state = get(listingStore);
      expect(state.title.value).toBe('User Title');
      expect(state.title.aiSuggested).toBe('AI Title');
      expect(state.title.userModified).toBe(true);
    });

    it('stores AI suggestion separately when user has modified field', () => {
      listingStore.setFieldValue('price', 400000);
      listingStore.setAISuggestion('price', 450000);
      
      const state = get(listingStore);
      expect(state.price.value).toBe(400000);
      expect(state.price.aiSuggested).toBe(450000);
    });

    it('overwrites AI value with new AI suggestion', () => {
      listingStore.setAISuggestion('bedrooms', 3);
      listingStore.setAISuggestion('bedrooms', 4);
      
      const state = get(listingStore);
      expect(state.bedrooms.value).toBe(4);
      expect(state.bedrooms.aiSuggested).toBe(4);
    });

    it('can set AI suggestion on field initialized with default', () => {
      listingStore.initField('bathrooms', 2);
      listingStore.setAISuggestion('bathrooms', 3);
      
      const state = get(listingStore);
      expect(state.bathrooms.value).toBe(3);
      expect(state.bathrooms.aiSuggested).toBe(3);
    });

    it('handles null AI suggestions', () => {
      listingStore.setAISuggestion('optional', null);
      
      const state = get(listingStore);
      expect(state.optional.value).toBeNull();
      expect(state.optional.aiSuggested).toBeNull();
    });

    it('handles boolean AI suggestions', () => {
      listingStore.setAISuggestion('petFriendly', true);
      
      const state = get(listingStore);
      expect(state.petFriendly.value).toBe(true);
    });

    it('updates only aiSuggested when user has modified field', () => {
      listingStore.setFieldValue('location', 'Downtown');
      const stateBefore = get(listingStore);
      const sourceBefore = stateBefore.location.source;
      
      listingStore.setAISuggestion('location', 'Uptown');
      
      const stateAfter = get(listingStore);
      expect(stateAfter.location.value).toBe('Downtown');
      expect(stateAfter.location.aiSuggested).toBe('Uptown');
      expect(stateAfter.location.source).toBe(sourceBefore);
      expect(stateAfter.location.userModified).toBe(true);
    });
  });

  describe('initField', () => {
    it('initializes field with default value', () => {
      listingStore.initField('status', 'draft');
      
      const state = get(listingStore);
      expect(state.status).toEqual({
        value: 'draft',
        userModified: false,
        source: 'default',
      });
    });

    it('initializes field with null when no default provided', () => {
      listingStore.initField('notes');
      
      const state = get(listingStore);
      expect(state.notes).toEqual({
        value: null,
        userModified: false,
        source: 'default',
      });
    });

    it('does not overwrite existing field', () => {
      listingStore.setFieldValue('title', 'Existing Title');
      listingStore.initField('title', 'Default Title');
      
      const state = get(listingStore);
      expect(state.title.value).toBe('Existing Title');
      expect(state.title.source).toBe('user');
    });

    it('does not overwrite AI-suggested field', () => {
      listingStore.setAISuggestion('description', 'AI Description');
      listingStore.initField('description', 'Default Description');
      
      const state = get(listingStore);
      expect(state.description.value).toBe('AI Description');
      expect(state.description.source).toBe('ai');
    });

    it('handles numeric default values', () => {
      listingStore.initField('floors', 2);
      
      const state = get(listingStore);
      expect(state.floors.value).toBe(2);
    });

    it('handles boolean default values', () => {
      listingStore.initField('published', false);
      
      const state = get(listingStore);
      expect(state.published.value).toBe(false);
    });

    it('initializes multiple fields independently', () => {
      listingStore.initField('status', 'draft');
      listingStore.initField('views', 0);
      listingStore.initField('featured', false);
      
      const state = get(listingStore);
      expect(state.status.value).toBe('draft');
      expect(state.views.value).toBe(0);
      expect(state.featured.value).toBe(false);
    });
  });

  describe('getFieldValue', () => {
    it('returns the value of an existing field', () => {
      listingStore.setFieldValue('title', 'Test House');
      
      const value = listingStore.getFieldValue('title');
      expect(value).toBe('Test House');
    });

    it('returns null for non-existent field', () => {
      const value = listingStore.getFieldValue('nonexistent');
      expect(value).toBeNull();
    });

    it('returns the current value, not AI suggestion', () => {
      listingStore.setFieldValue('price', 300000);
      listingStore.setAISuggestion('price', 350000);
      
      const value = listingStore.getFieldValue('price');
      expect(value).toBe(300000);
    });

    it('returns null value when field is explicitly set to null', () => {
      listingStore.setFieldValue('optional', null);
      
      const value = listingStore.getFieldValue('optional');
      expect(value).toBeNull();
    });

    it('returns false for boolean false value', () => {
      listingStore.setFieldValue('active', false);
      
      const value = listingStore.getFieldValue('active');
      expect(value).toBe(false);
    });

    it('returns 0 for zero number value', () => {
      listingStore.setFieldValue('commission', 0);
      
      const value = listingStore.getFieldValue('commission');
      expect(value).toBe(0);
    });

    it('returns empty string when set to empty string', () => {
      listingStore.setFieldValue('notes', '');
      
      const value = listingStore.getFieldValue('notes');
      expect(value).toBe('');
    });
  });

  describe('reset', () => {
    it('clears all fields', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.setFieldValue('price', 300000);
      listingStore.setAISuggestion('description', 'AI text');
      
      listingStore.reset();
      
      const state = get(listingStore);
      expect(state).toEqual({});
    });

    it('returns null for fields after reset', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.reset();
      
      const value = listingStore.getFieldValue('title');
      expect(value).toBeNull();
    });

    it('allows setting new values after reset', () => {
      listingStore.setFieldValue('title', 'Old House');
      listingStore.reset();
      listingStore.setFieldValue('title', 'New House');
      
      const value = listingStore.getFieldValue('title');
      expect(value).toBe('New House');
    });

    it('clears empty store without errors', () => {
      expect(() => listingStore.reset()).not.toThrow();
      
      const state = get(listingStore);
      expect(state).toEqual({});
    });
  });

  describe('loadState', () => {
    it('loads complete state from external source', () => {
      const externalState: ListingState = {
        title: {
          value: 'Loaded House',
          userModified: true,
          source: 'user',
        },
        price: {
          value: 400000,
          userModified: false,
          source: 'default',
        },
      };
      
      listingStore.loadState(externalState);
      
      const state = get(listingStore);
      expect(state).toEqual(externalState);
    });

    it('overwrites existing state', () => {
      listingStore.setFieldValue('title', 'Original');
      
      const newState: ListingState = {
        title: {
          value: 'Loaded',
          userModified: false,
          source: 'ai',
        },
      };
      
      listingStore.loadState(newState);
      
      const state = get(listingStore);
      expect(state.title.value).toBe('Loaded');
    });

    it('loads state with AI suggestions', () => {
      const stateWithAI: ListingState = {
        description: {
          value: 'User text',
          aiSuggested: 'AI text',
          userModified: true,
          source: 'user',
        },
      };
      
      listingStore.loadState(stateWithAI);
      
      const state = get(listingStore);
      expect(state.description.aiSuggested).toBe('AI text');
    });

    it('handles loading empty state', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.loadState({});
      
      const state = get(listingStore);
      expect(state).toEqual({});
    });

    it('loads state with mixed field types', () => {
      const mixedState: ListingState = {
        title: { value: 'House', userModified: true, source: 'user' },
        price: { value: 500000, userModified: false, source: 'ai' },
        furnished: { value: true, userModified: false, source: 'default' },
        notes: { value: null, userModified: false, source: 'default' },
      };
      
      listingStore.loadState(mixedState);
      
      const state = get(listingStore);
      expect(state.title.value).toBe('House');
      expect(state.price.value).toBe(500000);
      expect(state.furnished.value).toBe(true);
      expect(state.notes.value).toBeNull();
    });
  });

  describe('toJSON', () => {
    it('serializes fields to simple key-value object', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.setFieldValue('price', 300000);
      listingStore.setFieldValue('bedrooms', 3);
      
      const json = listingStore.toJSON();
      
      expect(json).toEqual({
        title: 'House',
        price: 300000,
        bedrooms: 3,
      });
    });

    it('includes only values, not metadata', () => {
      listingStore.setFieldValue('title', 'House');
      
      const json = listingStore.toJSON();
      
      expect(json.title).toBe('House');
      expect(json).not.toHaveProperty('userModified');
      expect(json).not.toHaveProperty('source');
      expect(json).not.toHaveProperty('aiSuggested');
    });

    it('returns empty object when store is empty', () => {
      const json = listingStore.toJSON();
      expect(json).toEqual({});
    });

    it('includes AI-suggested values if they are current', () => {
      listingStore.setAISuggestion('description', 'AI description');
      
      const json = listingStore.toJSON();
      expect(json.description).toBe('AI description');
    });

    it('includes user values over AI suggestions', () => {
      listingStore.setAISuggestion('title', 'AI Title');
      listingStore.setFieldValue('title', 'User Title');
      
      const json = listingStore.toJSON();
      expect(json.title).toBe('User Title');
    });

    it('handles null values', () => {
      listingStore.setFieldValue('optional', null);
      
      const json = listingStore.toJSON();
      expect(json.optional).toBeNull();
    });

    it('handles boolean values', () => {
      listingStore.setFieldValue('published', true);
      
      const json = listingStore.toJSON();
      expect(json.published).toBe(true);
    });

    it('handles zero values', () => {
      listingStore.setFieldValue('discount', 0);
      
      const json = listingStore.toJSON();
      expect(json.discount).toBe(0);
    });

    it('handles empty string values', () => {
      listingStore.setFieldValue('notes', '');
      
      const json = listingStore.toJSON();
      expect(json.notes).toBe('');
    });
  });

  describe('listingValues derived store', () => {
    it('derives simple values from state', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.setFieldValue('price', 300000);
      
      const values = get(listingValues);
      
      expect(values).toEqual({
        title: 'House',
        price: 300000,
      });
    });

    it('updates when store changes', () => {
      listingStore.setFieldValue('title', 'House A');
      let values = get(listingValues);
      expect(values.title).toBe('House A');
      
      listingStore.setFieldValue('title', 'House B');
      values = get(listingValues);
      expect(values.title).toBe('House B');
    });

    it('returns empty object when store is empty', () => {
      const values = get(listingValues);
      expect(values).toEqual({});
    });

    it('includes only current values, not AI suggestions', () => {
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title');
      
      const values = get(listingValues);
      expect(values.title).toBe('User Title');
    });

    it('reflects values from AI when no user modification', () => {
      listingStore.setAISuggestion('description', 'AI description');
      
      const values = get(listingValues);
      expect(values.description).toBe('AI description');
    });

    it('handles mixed value types', () => {
      listingStore.setFieldValue('title', 'House');
      listingStore.setFieldValue('price', 300000);
      listingStore.setFieldValue('furnished', true);
      listingStore.setFieldValue('notes', null);
      
      const values = get(listingValues);
      expect(values.title).toBe('House');
      expect(values.price).toBe(300000);
      expect(values.furnished).toBe(true);
      expect(values.notes).toBeNull();
    });
  });

  describe('aiSuggestions derived store', () => {
    it('returns suggestions that differ from current value', () => {
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title');
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({
        title: 'AI Title',
      });
    });

    it('excludes suggestions that match current value', () => {
      listingStore.setAISuggestion('description', 'Same text');
      listingStore.setFieldValue('description', 'Same text');
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({});
    });

    it('returns empty object when no AI suggestions exist', () => {
      listingStore.setFieldValue('title', 'House');
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({});
    });

    it('excludes fields without AI suggestions', () => {
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title');
      listingStore.setFieldValue('price', 300000);
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toHaveProperty('title');
      expect(suggestions).not.toHaveProperty('price');
    });

    it('updates when AI suggestions change', () => {
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title 1');
      
      let suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('AI Title 1');
      
      listingStore.setAISuggestion('title', 'AI Title 2');
      suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('AI Title 2');
    });

    it('updates when user value changes to differ from AI', () => {
      listingStore.setAISuggestion('price', 400000);
      let suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({});
      
      listingStore.setFieldValue('price', 350000);
      suggestions = get(aiSuggestions);
      expect(suggestions.price).toBe(400000);
    });

    it('removes suggestion when user accepts it', () => {
      listingStore.setFieldValue('title', 'Old Title');
      listingStore.setAISuggestion('title', 'New Title');
      
      let suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('New Title');
      
      // User accepts AI suggestion
      listingStore.setFieldValue('title', 'New Title');
      suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({});
    });

    it('handles multiple fields with different suggestion states', () => {
      // Field with different suggestion
      listingStore.setFieldValue('title', 'User Title');
      listingStore.setAISuggestion('title', 'AI Title');
      
      // Field with matching suggestion
      listingStore.setAISuggestion('description', 'Same');
      listingStore.setFieldValue('description', 'Same');
      
      // Field without suggestion
      listingStore.setFieldValue('price', 300000);
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({
        title: 'AI Title',
      });
    });
  });

  describe('Complex workflows', () => {
    it('handles complete form filling workflow', () => {
      // Initialize with defaults
      listingStore.initField('status', 'draft');
      listingStore.initField('views', 0);
      
      // AI provides suggestions
      listingStore.setAISuggestion('title', 'Luxury Apartment');
      listingStore.setAISuggestion('description', 'Beautiful apartment in downtown');
      
      // User modifies some AI suggestions
      listingStore.setFieldValue('title', 'Premium Apartment');
      
      // User adds additional fields
      listingStore.setFieldValue('price', 500000);
      listingStore.setFieldValue('bedrooms', 2);
      
      // Verify final state
      const json = listingStore.toJSON();
      expect(json.status).toBe('draft');
      expect(json.title).toBe('Premium Apartment');
      expect(json.description).toBe('Beautiful apartment in downtown');
      expect(json.price).toBe(500000);
      
      // Verify AI suggestions still available
      const suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('Luxury Apartment');
      expect(suggestions).not.toHaveProperty('description');
    });

    it('handles save and reload workflow', () => {
      // Initial data entry
      listingStore.setFieldValue('title', 'My House');
      listingStore.setFieldValue('price', 400000);
      listingStore.setAISuggestion('description', 'AI generated');
      
      // Simulate save
      const savedState = get(listingStore);
      
      // Simulate page reload
      listingStore.reset();
      expect(get(listingStore)).toEqual({});
      
      // Restore saved state
      listingStore.loadState(savedState);
      
      // Verify state is restored
      expect(listingStore.getFieldValue('title')).toBe('My House');
      expect(listingStore.getFieldValue('price')).toBe(400000);
      expect(listingStore.getFieldValue('description')).toBe('AI generated');
    });

    it('handles AI re-suggesting after user modification', () => {
      // User enters value
      listingStore.setFieldValue('title', 'House 1');
      
      // AI suggests different value
      listingStore.setAISuggestion('title', 'Beautiful House');
      
      // User value should be preserved
      expect(listingStore.getFieldValue('title')).toBe('House 1');
      
      // AI suggestion should be available
      const suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('Beautiful House');
      
      // AI suggests again (different value)
      listingStore.setAISuggestion('title', 'Luxury House');
      
      // User value still preserved, new suggestion available
      expect(listingStore.getFieldValue('title')).toBe('House 1');
      const newSuggestions = get(aiSuggestions);
      expect(newSuggestions.title).toBe('Luxury House');
    });

    it('handles multiple derived store subscriptions', () => {
      listingStore.setFieldValue('title', 'Test House');
      listingStore.setAISuggestion('description', 'AI text');
      
      const values = get(listingValues);
      const suggestions = get(aiSuggestions);
      
      expect(values.title).toBe('Test House');
      expect(values.description).toBe('AI text');
      expect(suggestions).toEqual({});
    });
  });

  describe('Edge cases and error handling', () => {
    it('handles rapid successive updates to same field', () => {
      listingStore.setFieldValue('counter', 1);
      listingStore.setFieldValue('counter', 2);
      listingStore.setFieldValue('counter', 3);
      listingStore.setFieldValue('counter', 4);
      
      expect(listingStore.getFieldValue('counter')).toBe(4);
    });

    it('handles very long string values', () => {
      const longString = 'a'.repeat(10000);
      listingStore.setFieldValue('description', longString);
      
      expect(listingStore.getFieldValue('description')).toBe(longString);
    });

    it('handles special characters in field IDs', () => {
      listingStore.setFieldValue('field-with-dashes', 'value1');
      listingStore.setFieldValue('field_with_underscores', 'value2');
      listingStore.setFieldValue('field.with.dots', 'value3');
      
      expect(listingStore.getFieldValue('field-with-dashes')).toBe('value1');
      expect(listingStore.getFieldValue('field_with_underscores')).toBe('value2');
      expect(listingStore.getFieldValue('field.with.dots')).toBe('value3');
    });

    it('handles unicode characters in values', () => {
      listingStore.setFieldValue('title', '🏠 Beautiful House 中文');
      expect(listingStore.getFieldValue('title')).toBe('🏠 Beautiful House 中文');
    });

    it('handles negative numbers', () => {
      listingStore.setFieldValue('adjustment', -50);
      expect(listingStore.getFieldValue('adjustment')).toBe(-50);
    });

    it('handles very large numbers', () => {
      listingStore.setFieldValue('price', 999999999999);
      expect(listingStore.getFieldValue('price')).toBe(999999999999);
    });

    it('handles decimal numbers', () => {
      listingStore.setFieldValue('commission', 2.5);
      expect(listingStore.getFieldValue('commission')).toBe(2.5);
    });

    it('preserves field isolation - modifying one does not affect others', () => {
      listingStore.setFieldValue('field1', 'value1');
      listingStore.setFieldValue('field2', 'value2');
      
      listingStore.setFieldValue('field1', 'updated1');
      
      expect(listingStore.getFieldValue('field1')).toBe('updated1');
      expect(listingStore.getFieldValue('field2')).toBe('value2');
    });

    it('handles alternating between user and AI updates', () => {
      listingStore.setFieldValue('title', 'User 1');
      listingStore.setAISuggestion('title', 'AI 1');
      listingStore.setFieldValue('title', 'User 2');
      listingStore.setAISuggestion('title', 'AI 2');
      
      expect(listingStore.getFieldValue('title')).toBe('User 2');
      const suggestions = get(aiSuggestions);
      expect(suggestions.title).toBe('AI 2');
    });

    it('handles store access without any initialization', () => {
      const value = listingStore.getFieldValue('nonexistent');
      expect(value).toBeNull();
      
      const json = listingStore.toJSON();
      expect(json).toEqual({});
      
      const values = get(listingValues);
      expect(values).toEqual({});
      
      const suggestions = get(aiSuggestions);
      expect(suggestions).toEqual({});
    });
  });
});
