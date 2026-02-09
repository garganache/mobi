<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { getComponent } from './fields/registry';
  import { listingStore } from '../stores/listingStore';
  import type { FieldValue } from '../stores/listingStore';

  /**
   * Field schema definition
   */
  export interface FieldSchema {
    id: string;
    component_type: string;
    label: string;
    placeholder?: string;
    options?: { value: string; label: string }[];
    min?: number;
    max?: number;
    step?: number;
    default?: FieldValue;
  }

  /**
   * UI schema array from backend
   */
  export let schema: FieldSchema[] = [];

  /**
   * Animation duration for new fields
   */
  export let animationDuration = 300;

  // Initialize fields with defaults when schema changes
  $: {
    schema.forEach(field => {
      listingStore.initField(field.id, field.default ?? null);
    });
  }

  // Get the value for a field from the store
  function getFieldValue(fieldId: string): FieldValue {
    return $listingStore[fieldId]?.value ?? null;
  }

  // Update the store when a field value changes
  function handleFieldChange(fieldId: string, event: CustomEvent | Event) {
    const target = event.target as HTMLInputElement | HTMLSelectElement;
    let value: FieldValue;

    if (target.type === 'checkbox') {
      value = (target as HTMLInputElement).checked;
    } else if (target.type === 'number') {
      value = target.value ? parseFloat(target.value) : null;
    } else {
      value = target.value;
    }

    listingStore.setFieldValue(fieldId, value);
  }
</script>

<div class="dynamic-form">
  {#each schema as field, index (field.id)}
    {@const component = getComponent(field.component_type)}
    
    <div
      class="field-container"
      in:fly={{ y: 20, duration: animationDuration, delay: index * 50 }}
      out:fade={{ duration: 200 }}
    >
      {#if component}
        <svelte:component
          this={component}
          id={field.id}
          label={field.label}
          bind:value={$listingStore[field.id].value}
          placeholder={field.placeholder}
          options={field.options}
          min={field.min}
          max={field.max}
          step={field.step}
        />
      {:else}
        <div class="unknown-field-type" role="alert">
          <strong>Unknown field type:</strong> {field.component_type}
          <br/>
          <small>Field ID: {field.id}</small>
        </div>
      {/if}
    </div>
  {/each}

  {#if schema.length === 0}
    <div class="empty-state">
      <p>No fields to display. Add some data to get started.</p>
    </div>
  {/if}
</div>

<style>
  .dynamic-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .field-container {
    width: 100%;
  }

  .unknown-field-type {
    padding: 1rem;
    background-color: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 0.375rem;
    color: #92400e;
  }

  .unknown-field-type strong {
    color: #78350f;
  }

  .unknown-field-type small {
    color: #a16207;
  }

  .empty-state {
    padding: 2rem;
    text-align: center;
    color: #6b7280;
  }

  .empty-state p {
    margin: 0;
  }
</style>
