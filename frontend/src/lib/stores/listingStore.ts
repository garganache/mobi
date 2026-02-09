/**
 * Listing Store
 * 
 * Manages the state for property listing form data.
 * Tracks both user-entered values and AI-suggested values.
 */

import { writable, derived, get } from 'svelte/store';

/**
 * Field value can be of various types
 */
export type FieldValue = string | number | boolean | null;

/**
 * Single field state with metadata
 */
export interface FieldState {
  value: FieldValue;
  aiSuggested?: FieldValue;
  userModified: boolean;
  source: 'user' | 'ai' | 'default';
}

/**
 * Complete listing form state
 */
export interface ListingState {
  [fieldId: string]: FieldState;
}

/**
 * Create the initial state
 */
function createListingStore() {
  const { subscribe, set, update } = writable<ListingState>({});

  return {
    subscribe,
    
    /**
     * Set a field value (from user input)
     */
    setFieldValue: (fieldId: string, value: FieldValue) => {
      update(state => ({
        ...state,
        [fieldId]: {
          value,
          userModified: true,
          source: 'user',
          aiSuggested: state[fieldId]?.aiSuggested,
        }
      }));
    },

    /**
     * Set an AI-suggested value for a field
     */
    setAISuggestion: (fieldId: string, value: FieldValue) => {
      update(state => {
        const existing = state[fieldId];
        
        // If user hasn't modified this field, use AI suggestion
        if (!existing || !existing.userModified) {
          return {
            ...state,
            [fieldId]: {
              value,
              aiSuggested: value,
              userModified: false,
              source: 'ai',
            }
          };
        }
        
        // Otherwise, just store as suggestion without overwriting user value
        return {
          ...state,
          [fieldId]: {
            ...existing,
            aiSuggested: value,
          }
        };
      });
    },

    /**
     * Initialize a field with a default value
     */
    initField: (fieldId: string, defaultValue: FieldValue = null) => {
      update(state => {
        // Don't overwrite existing state
        if (state[fieldId]) return state;
        
        return {
          ...state,
          [fieldId]: {
            value: defaultValue,
            userModified: false,
            source: 'default',
          }
        };
      });
    },

    /**
     * Get the current value of a field
     */
    getFieldValue: (fieldId: string): FieldValue => {
      const state = get(listingStore);
      return state[fieldId]?.value ?? null;
    },

    /**
     * Reset all form data
     */
    reset: () => {
      set({});
    },

    /**
     * Load state from external source (e.g., saved listing)
     */
    loadState: (state: ListingState) => {
      set(state);
    },

    /**
     * Serialize to JSON for sending to backend
     */
    toJSON: (): Record<string, FieldValue> => {
      const state = get(listingStore);
      const result: Record<string, FieldValue> = {};
      
      for (const [fieldId, fieldState] of Object.entries(state)) {
        result[fieldId] = fieldState.value;
      }
      
      return result;
    },
  };
}

export const listingStore = createListingStore();

/**
 * Derived store: just the values (for easy serialization)
 */
export const listingValues = derived(
  listingStore,
  ($state) => {
    const result: Record<string, FieldValue> = {};
    for (const [fieldId, fieldState] of Object.entries($state)) {
      result[fieldId] = fieldState.value;
    }
    return result;
  }
);

/**
 * Derived store: fields that have AI suggestions different from current value
 */
export const aiSuggestions = derived(
  listingStore,
  ($state) => {
    const result: Record<string, FieldValue> = {};
    for (const [fieldId, fieldState] of Object.entries($state)) {
      if (fieldState.aiSuggested !== undefined && 
          fieldState.aiSuggested !== fieldState.value) {
        result[fieldId] = fieldState.aiSuggested;
      }
    }
    return result;
  }
);
