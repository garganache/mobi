<script lang="ts">
  import DynamicForm from './DynamicForm.svelte';
  import type { FieldSchema } from './DynamicForm.svelte';
  import { listingStore, listingValues } from '../stores/listingStore';

  // Mock schema for testing
  let schema: FieldSchema[] = [
    {
      id: 'property_type',
      component_type: 'select',
      label: 'Property Type',
      placeholder: 'Select property type',
      options: [
        { value: 'apartment', label: 'Apartment' },
        { value: 'house', label: 'House' },
        { value: 'condo', label: 'Condo' },
      ],
    },
    {
      id: 'address',
      component_type: 'text',
      label: 'Address',
      placeholder: 'Enter property address',
    },
    {
      id: 'bedrooms',
      component_type: 'number',
      label: 'Number of Bedrooms',
      placeholder: '0',
      min: 0,
      max: 20,
    },
    {
      id: 'has_pool',
      component_type: 'toggle',
      label: 'Has Swimming Pool',
    },
  ];

  function addField() {
    schema = [
      ...schema,
      {
        id: `custom_field_${Date.now()}`,
        component_type: 'text',
        label: 'Custom Field',
        placeholder: 'Enter value',
      },
    ];
  }

  function logState() {
    console.log('Current State:', $listingValues);
    console.log('Full State:', $listingStore);
    console.log('JSON:', listingStore.toJSON());
  }

  function resetForm() {
    listingStore.reset();
  }
</script>

<div class="demo-container">
  <h2>Dynamic Listing Form Demo</h2>
  
  <DynamicForm {schema} />

  <div class="controls">
    <button on:click={addField}>Add Field</button>
    <button on:click={logState}>Log State</button>
    <button on:click={resetForm}>Reset</button>
  </div>

  <div class="state-display">
    <h3>Current Values:</h3>
    <pre>{JSON.stringify($listingValues, null, 2)}</pre>
  </div>
</div>

<style>
  .demo-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
  }

  h2 {
    margin-bottom: 1.5rem;
    color: #1f2937;
  }

  h3 {
    margin-top: 2rem;
    margin-bottom: 0.5rem;
    color: #374151;
    font-size: 1rem;
  }

  .controls {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.5rem;
  }

  button {
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background-color: #2563eb;
  }

  button:active {
    background-color: #1d4ed8;
  }

  .state-display {
    margin-top: 1.5rem;
    padding: 1rem;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.375rem;
  }

  pre {
    margin: 0;
    font-size: 0.875rem;
    overflow-x: auto;
  }
</style>
