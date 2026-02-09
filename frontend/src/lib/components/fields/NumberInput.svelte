<script lang="ts">
  export let id: string;
  export let label: string;
  export let value: number | null = null;
  export let placeholder: string = '';
  export let min: number | undefined = undefined;
  export let max: number | undefined = undefined;
  export let step: number = 1;
  export let error: string | null = null;
</script>

<div class="field-wrapper">
  <label for={id} class="field-label">{label}</label>
  <input
    {id}
    type="number"
    bind:value
    {placeholder}
    {min}
    {max}
    {step}
    class="field-input"
    class:error={!!error}
    aria-label={label}
    aria-invalid={!!error}
    aria-describedby={error ? `${id}-error` : undefined}
  />
  {#if error}
    <span id="{id}-error" class="field-error" role="alert">{error}</span>
  {/if}
</div>

<style>
  .field-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .field-label {
    font-weight: 500;
    font-size: 0.875rem;
    color: #374151;
  }

  .field-input {
    padding: 0.5rem 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  }

  .field-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .field-input.error {
    border-color: #ef4444;
  }

  .field-input.error:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
  }

  .field-error {
    font-size: 0.875rem;
    color: #ef4444;
  }
</style>
