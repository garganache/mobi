<script lang="ts">
  export let id: string;
  export let label: string;
  export let value: boolean = false;
  export let error: string | null = null;
</script>

<div class="field-wrapper">
  <div class="toggle-container">
    <label for={id} class="field-label">{label}</label>
    <button
      type="button"
      role="switch"
      {id}
      class="toggle"
      class:active={value}
      aria-checked={value}
      aria-label={label}
      on:click={() => value = !value}
    >
      <span class="toggle-slider" class:active={value}></span>
    </button>
  </div>
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

  .toggle-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .field-label {
    font-weight: 500;
    font-size: 0.875rem;
    color: #374151;
  }

  .toggle {
    position: relative;
    width: 3rem;
    height: 1.75rem;
    background-color: #d1d5db;
    border-radius: 9999px;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s ease-in-out;
    padding: 0;
  }

  .toggle:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .toggle.active {
    background-color: #3b82f6;
  }

  .toggle-slider {
    position: absolute;
    top: 0.125rem;
    left: 0.125rem;
    width: 1.5rem;
    height: 1.5rem;
    background-color: white;
    border-radius: 9999px;
    transition: transform 0.2s ease-in-out;
  }

  .toggle-slider.active {
    transform: translateX(1.25rem);
  }

  .field-error {
    font-size: 0.875rem;
    color: #ef4444;
  }
</style>
