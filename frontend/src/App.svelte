<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import ImageUpload from './lib/components/ImageUpload.svelte';
  import AIMessage from './lib/components/AIMessage.svelte';
  import AnimatedDynamicForm from './lib/components/AnimatedDynamicForm.svelte';
  import { listingStore } from './lib/stores/listingStore';
  import type { FieldSchema } from './lib/components/AnimatedDynamicForm.svelte';

  interface AnalyzeStepResponse {
    extracted_data: Record<string, any>;
    ui_schema: FieldSchema[];
    ai_message?: string;
    step_number?: number;
    completion_percentage?: number;
  }

  let currentStep = 0;
  let completionPercentage = 0;
  let aiMessage = 'Drop a photo to start your listing';
  let formSchema: FieldSchema[] = [];
  let isLoading = false;
  let error: string | null = null;

  // Load saved state on mount
  onMount(() => {
    loadSavedState();
  });

  async function handleImageUpload(event: CustomEvent) {
    const { response } = event.detail;
    await handleAnalyzeResponse(response);
  }

  async function handleFieldUpdate() {
    await analyzeStep('field_update');
  }

  async function analyzeStep(inputType: 'image' | 'text' | 'field_update', inputData?: string) {
    isLoading = true;
    error = null;

    try {
      const response = await fetch('/api/analyze-step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_type: inputType,
          new_input: inputData || null,
          current_data: listingStore.toJSON()
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Analysis failed' }));
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const result = await response.json();
      await handleAnalyzeResponse(result);

    } catch (err) {
      error = err instanceof Error ? err.message : 'Analysis failed';
      console.error('Analysis error:', err);
    } finally {
      isLoading = false;
    }
  }

  async function handleAnalyzeResponse(response: AnalyzeStepResponse) {
    // Update form state with extracted data
    if (response.extracted_data) {
      Object.entries(response.extracted_data).forEach(([fieldId, value]) => {
        listingStore.setFieldValue(fieldId, value);
      });
    }

    // Update UI schema (this will trigger animations)
    formSchema = response.ui_schema || [];
    
    // Update AI message
    aiMessage = response.ai_message || '';
    
    // Update progress
    currentStep = response.step_number || 0;
    completionPercentage = response.completion_percentage || 0;

    // Save current state
    saveCurrentState();
  }

  function saveCurrentState() {
    const state = {
      formData: listingStore.toJSON(),
      schema: formSchema,
      aiMessage,
      currentStep,
      completionPercentage
    };
    localStorage.setItem('mobi_listing_state', JSON.stringify(state));
  }

  function loadSavedState() {
    const saved = localStorage.getItem('mobi_listing_state');
    if (saved) {
      try {
        const state = JSON.parse(saved);
        listingStore.loadState(state.formData);
        formSchema = state.schema || [];
        aiMessage = state.aiMessage || '';
        currentStep = state.currentStep || 0;
        completionPercentage = state.completionPercentage || 0;
      } catch (e) {
        console.warn('Failed to load saved state:', e);
      }
    }
  }

  function resetForm() {
    if (confirm('Are you sure you want to reset the form? This will clear all data.')) {
      listingStore.reset();
      formSchema = [];
      aiMessage = '';
      currentStep = 0;
      completionPercentage = 0;
      localStorage.removeItem('mobi_listing_state');
    }
  }

  // Note: Removed auto-subscribe to prevent infinite loop.
  // User triggers updates manually via "Continue" button.
</script>

<main>
  <header class="app-header">
    <h1>Mobi Property Listing</h1>
    <div class="header-actions">
      {#if completionPercentage > 0}
        <div class="progress-indicator">
          <span class="progress-text">{Math.round(completionPercentage)}% Complete</span>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {completionPercentage}%"></div>
          </div>
        </div>
      {/if}
      <button class="reset-button" on:click={resetForm} title="Reset form">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  </header>

  <div class="app-content">
    {#if aiMessage}
      <div class="ai-message-container" in:fly={{ y: -20, duration: 400 }}>
        <AIMessage 
          message={aiMessage} 
          avatar="ai"
          typing={isLoading}
        />
      </div>
    {/if}

    {#if formSchema.length === 0}
      <!-- Initial state - show image upload -->
      <div class="initial-upload" in:fade={{ duration: 500 }}>
        <div class="upload-section">
          <h2>Get Started</h2>
          <p>Upload an image of your property to begin creating your listing</p>
          <ImageUpload 
            on:uploadSuccess={handleImageUpload}
            on:uploadError={(e) => error = e.detail.error}
          />
        </div>
      </div>
    {:else}
      <!-- Progressive form -->
      <div class="progressive-form" in:fade={{ duration: 500 }}>
        <div class="form-container">
          <AnimatedDynamicForm 
            schema={formSchema}
            animationDuration={400}
            staggerDelay={80}
            highlightNewFields={true}
          />
        </div>

        <div class="actions-section">
          <button 
            class="submit-button"
            disabled={isLoading}
            on:click={() => analyzeStep('field_update')}
          >
            {isLoading ? 'Processing...' : 'Continue'}
          </button>
        </div>
      </div>
    {/if}

    {#if error}
      <div class="error-message" in:fade={{ duration: 300 }}>
        <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {error}
        <button class="dismiss-error" on:click={() => error = null}>×</button>
      </div>
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #fafafa;
    color: #1a1a1a;
  }

  main {
    min-height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .app-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .progress-indicator {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
  }

  .progress-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #6b7280;
  }

  .progress-bar {
    width: 100px;
    height: 4px;
    background: #e5e7eb;
    border-radius: 2px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
    transition: width 0.5s ease;
  }

  .reset-button {
    background: none;
    border: none;
    padding: 0.5rem;
    border-radius: 0.375rem;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s ease;
  }

  .reset-button:hover {
    background: #f3f4f6;
    color: #374151;
  }

  .reset-button svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .app-content {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .initial-upload {
    text-align: center;
    padding: 3rem 0;
  }

  .upload-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 0.5rem;
  }

  .upload-section p {
    color: #6b7280;
    margin-bottom: 2rem;
  }

  .progressive-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .ai-message-container {
    margin-bottom: 1rem;
  }

  .form-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .actions-section {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
  }

  .submit-button {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
  }

  .submit-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 8px 15px -3px rgba(59, 130, 246, 0.4);
  }

  .submit-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .error-message {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #dc2626;
    margin-top: 1rem;
  }

  .error-icon {
    width: 1.25rem;
    height: 1.25rem;
    flex-shrink: 0;
  }

  .dismiss-error {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #dc2626;
    margin-left: auto;
    padding: 0;
    width: 1.5rem;
    height: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    main {
      padding: 1rem;
    }

    .app-header {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }

    .header-actions {
      width: 100%;
      justify-content: center;
    }

    .form-container {
      padding: 1.5rem;
    }
  }

  @media (max-width: 480px) {
    main {
      padding: 0.5rem;
    }

    .app-header h1 {
      font-size: 1.5rem;
    }

    .form-container {
      padding: 1rem;
    }
  }
</style>