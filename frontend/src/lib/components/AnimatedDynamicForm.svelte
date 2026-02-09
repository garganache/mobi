<script lang="ts">
  import { fly, fade, scale, slide } from 'svelte/transition';
  import { quintOut, quadInOut } from 'svelte/easing';
  import { flip } from 'svelte/animate';
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
    required?: boolean;
  }

  /**
   * UI schema array from backend
   */
  export let schema: FieldSchema[] = [];

  /**
   * Animation configuration
   */
  export let animationDuration = 400;
  export let staggerDelay = 80;
  export let highlightNewFields = true;
  export let highlightDuration = 2000;

  // Track which fields are newly added
  let previousFieldIds: Set<string> = new Set();
  let newFieldIds: Set<string> = new Set();

  // Initialize fields with defaults when schema changes
  $: {
    // Detect new fields
    const currentFieldIds = new Set(schema.map(f => f.id));
    newFieldIds = new Set([...currentFieldIds].filter(id => !previousFieldIds.has(id)));
    previousFieldIds = currentFieldIds;

    // Highlight new fields if enabled
    if (highlightNewFields && newFieldIds.size > 0) {
      setTimeout(() => {
        newFieldIds.clear();
        newFieldIds = new Set(newFieldIds); // Trigger reactivity
      }, highlightDuration);
    }

    // Initialize new fields with defaults
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

  // Check if a field is newly added
  function isNewField(fieldId: string): boolean {
    return newFieldIds.has(fieldId);
  }

  // Custom transition for field entrance
  function fieldTransition(node: Element, params: { delay: number }) {
    return {
      duration: animationDuration,
      easing: quintOut,
      css: (t: number, u: number) => `
        transform: translateY(${u * 20}px);
        opacity: ${t};
        transition-property: transform, opacity;
      `
    };
  }

  // Highlight animation for new fields
  function highlightTransition(node: Element) {
    return {
      duration: highlightDuration,
      css: (t: number) => {
        const glow = 0.3 + (t * 0.7);
        return `
          box-shadow: 0 0 ${glow * 20}px rgba(59, 130, 246, ${glow * 0.5});
          border-color: rgba(59, 130, 246, ${glow * 0.7});
        `;
      }
    };
  }
</script>

<div class="dynamic-form">
  {#each schema as field, index (field.id)}
    {@const component = getComponent(field.component_type)}
    {@const isNew = isNewField(field.id)}
    
    <div
      class="field-container {isNew ? 'new-field' : ''}"
      in:fieldTransition={{ delay: index * staggerDelay }}
      out:fade={{ duration: animationDuration / 2 }}
      animate:flip={{ duration: animationDuration / 2 }}
    >
      {#if component}
        <div 
          class="field-wrapper {isNew ? 'highlight-field' : ''}"
          in:highlightTransition
        >
          <svelte:component
            this={component}
            id={field.id}
            label={field.label}
            bind:value={$listingStore[field.id]?.value}
            placeholder={field.placeholder}
            options={field.options}
            min={field.min}
            max={field.max}
            step={field.step}
            required={field.required}
            on:change={(e) => handleFieldChange(field.id, e)}
          />
          
          {#if isNew && highlightNewFields}
            <div class="new-field-indicator" in:fade={{ delay: 300 }}>
              <span class="new-badge">New</span>
            </div>
          {/if}
        </div>
      {:else}
        <div class="unknown-field-type" role="alert" in:fade={{ delay: index * 50 }}>
          <strong>Unknown field type:</strong> {field.component_type}
          <br/>
          <small>Field ID: {field.id}</small>
        </div>
      {/if}
    </div>
  {/each}

  {#if schema.length === 0}
    <div class="empty-state" in:fade={{ duration: animationDuration }}>
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <p>Ready to help you create your listing</p>
      <small>Upload an image or start filling in details to get started</small>
    </div>
  {/if}
</div>

<style>
  .dynamic-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    padding: 1rem 0;
  }

  .field-container {
    width: 100%;
    position: relative;
  }

  .field-wrapper {
    position: relative;
    transition: all 0.3s ease;
  }

  .field-wrapper.highlight-field {
    border-radius: 0.5rem;
    padding: 0.25rem;
    background: rgba(59, 130, 246, 0.05);
    border: 2px solid transparent;
  }

  .new-field-indicator {
    position: absolute;
    top: -0.5rem;
    right: -0.5rem;
    z-index: 10;
  }

  .new-badge {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.05);
      opacity: 0.8;
    }
  }

  .unknown-field-type {
    padding: 1rem;
    background-color: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 0.5rem;
    color: #92400e;
    animation: shake 0.5s ease-in-out;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-2px); }
    75% { transform: translateX(2px); }
  }

  .unknown-field-type strong {
    color: #78350f;
  }

  .unknown-field-type small {
    color: #a16207;
  }

  .empty-state {
    padding: 3rem 2rem;
    text-align: center;
    color: #6b7280;
    background: #f9fafb;
    border: 2px dashed #d1d5db;
    border-radius: 1rem;
    margin: 2rem 0;
  }

  .empty-icon {
    width: 3rem;
    height: 3rem;
    margin: 0 auto 1rem;
    color: #9ca3af;
  }

  .empty-icon svg {
    width: 100%;
    height: 100%;
  }

  .empty-state p {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 500;
    color: #374151;
  }

  .empty-state small {
    font-size: 0.875rem;
    color: #6b7280;
  }

  /* Field entrance animations */
  .field-container.new-field {
    animation: fieldEntrance 0.6s ease-out;
  }

  @keyframes fieldEntrance {
    0% {
      opacity: 0;
      transform: translateY(30px) scale(0.95);
    }
    50% {
      opacity: 0.7;
      transform: translateY(-5px) scale(1.02);
    }
    100% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  /* Smooth container height transitions */
  :global(.dynamic-form) {
    container-type: inline-size;
  }

  /* Responsive design */
  @media (max-width: 640px) {
    .dynamic-form {
      gap: 0.75rem;
    }

    .field-wrapper.highlight-field {
      padding: 0.125rem;
    }

    .new-badge {
      font-size: 0.625rem;
      padding: 0.125rem 0.5rem;
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .empty-state {
      background: #1f2937;
      border-color: #4b5563;
      color: #9ca3af;
    }

    .empty-state p {
      color: #f3f4f6;
    }

    .unknown-field-type {
      background-color: #451a00;
      border-color: #92400e;
      color: #fed7aa;
    }

    .unknown-field-type strong {
      color: #fed7aa;
    }

    .field-wrapper.highlight-field {
      background: rgba(59, 130, 246, 0.1);
    }
  }

  /* Reduced motion support */
  @media (prefers-reduced-motion: reduce) {
    .field-wrapper {
      transition: none;
    }

    .new-badge {
      animation: none;
    }

    .field-container.new-field {
      animation: none;
    }

    .unknown-field-type {
      animation: none;
    }
  }
</style>