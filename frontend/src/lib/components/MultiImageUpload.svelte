<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { t } from '$lib/i18n';
  import VisionAnalysisDisplay from './VisionAnalysisDisplay.svelte';

  export let maxFileSize = 10 * 1024 * 1024; // 10MB
  export let acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  export let maxImages = 10;
  
  interface ImageUpload {
    id: string;
    file: File;
    previewUrl: string;
    isUploading: boolean;
    progress: number;
    error: string | null;
    isComplete?: boolean;
  }

  let uploads: ImageUpload[] = [];
  let isDragging = false;
  let error: string | null = null;
  let isAnalyzing = false;
  let synthesis: any | null = null;

  const dispatch = createEventDispatcher<{
    analysisComplete: { synthesis: any; individualAnalyses: any[] };
    uploadError: { error: string };
  }>();

  function validateFile(file: File): string | null {
    if (!acceptedTypes.includes(file.type)) {
      return `Invalid file type. Please upload: ${acceptedTypes.map(t => t.split('/')[1]).join(', ')}`;
    }
    if (file.size > maxFileSize) {
      return `File too large. Maximum size is ${maxFileSize / (1024 * 1024)}MB`;
    }
    return null;
  }

  function generateId(): string {
    return `upload-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  function handleFileSelect(selectedFiles: File[]) {
    error = null;
    
    console.log('handleFileSelect called with', selectedFiles.length, 'files');
    console.log('Current uploads before filtering:', uploads.length);
    
    const validFiles: File[] = [];
    
    for (const file of selectedFiles) {
      const validationError = validateFile(file);
      if (validationError) {
        error = validationError;
        continue;
      }
      validFiles.push(file);
    }
    
    if (validFiles.length === 0) return;
    
    // Check if we have room for more images (only count active uploads, not completed ones)
    const activeUploads = uploads.filter(u => !u.isComplete);
    console.log('Active uploads (not completed):', activeUploads.length);
    if (activeUploads.length + validFiles.length > maxImages) {
      error = `Maximum ${maxImages} images allowed. You can add ${maxImages - activeUploads.length} more.`;
      return;
    }
    
    // Clear any existing completed uploads before adding new ones
    // This prevents accumulation of old completed uploads
    uploads = uploads.filter(u => !u.isComplete);
    console.log('After filtering out completed uploads:', uploads.length);
    
    // Create upload entries
    const newUploads: ImageUpload[] = validFiles.map(file => ({
      id: generateId(),
      file,
      previewUrl: URL.createObjectURL(file),
      isUploading: false,
      progress: 0,
      error: null,
    }));
    
    uploads = [...uploads, ...newUploads];
    console.log('Final uploads count after adding new files:', uploads.length);
  }

  async function analyzeAllImages() {
    if (uploads.length === 0) return;
    
    console.log('Before analysis, uploads.length:', uploads.length);
    isAnalyzing = true;
    error = null;
    synthesis = null;
    
    // Show progress for all images
    uploads = uploads.map(u => ({ ...u, isUploading: true, progress: 0 }));
    
    try {
      // Create FormData with all images
      const formData = new FormData();
      uploads.forEach(upload => {
        formData.append('files', upload.file);
      });
      
      // Update progress
      const progressInterval = setInterval(() => {
        uploads = uploads.map(u => ({
          ...u,
          progress: Math.min(u.progress + 5, 95)
        }));
      }, 200);
      
      const response = await fetch('/api/analyze-batch', {
        method: 'POST',
        body: formData
      });
      
      clearInterval(progressInterval);
      
      if (!response.ok) {
        let errorMessage = 'Analysis failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If JSON parsing fails, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      const result = await response.json();
      
      // Mark all uploads as complete
      uploads = uploads.map(u => ({
        ...u,
        isUploading: false,
        progress: 100,
        isComplete: true
      }));
      
      console.log('After analysis, uploads.length:', uploads.length);
      
      // Store synthesis result
      synthesis = result.synthesis;
      
      // Dispatch completion event FIRST
      dispatch('analysisComplete', { 
        synthesis: result.synthesis,
        individualAnalyses: result.individual_analyses,
        imageUrls: uploads.map(u => u.previewUrl)  // Pass image URLs
      });
      
      // THEN immediately clear uploads (no delay to prevent duplication)
      clearAll();
      console.log('After clearAll, uploads.length:', uploads.length);
      
    } catch (err) {
      clearInterval(progressInterval);
      const errorMsg = err instanceof Error ? err.message : 'Analysis failed';
      error = errorMsg;
      
      // Mark all uploads as failed
      uploads = uploads.map(u => ({
        ...u,
        isUploading: false,
        progress: 0,
        error: errorMsg
      }));
      
      dispatch('uploadError', { error: errorMsg });
    } finally {
      isAnalyzing = false;
    }
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging = false;
    
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const fileArray = Array.from(files);
      handleFileSelect(fileArray);
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    isDragging = true;
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    isDragging = false;
  }

  function handleFileInput(e: Event) {
    const target = e.target as HTMLInputElement;
    const files = target.files;
    if (files && files.length > 0) {
      const fileArray = Array.from(files);
      handleFileSelect(fileArray);
    }
    // Reset input so the same file can be selected again
    target.value = '';
  }

  function removeUpload(id: string) {
    const upload = uploads.find(u => u.id === id);
    if (upload) {
      URL.revokeObjectURL(upload.previewUrl);
    }
    uploads = uploads.filter(u => u.id !== id);
    
    // If we removed all uploads, clear synthesis
    if (uploads.length === 0) {
      synthesis = null;
    }
  }

  function clearAll() {
    console.log('clearAll() called, current uploads.length:', uploads.length);
    uploads.forEach(upload => {
      URL.revokeObjectURL(upload.previewUrl);
    });
    uploads = [];
    synthesis = null;
    error = null;
    isAnalyzing = false;
    console.log('After clearAll, uploads.length:', uploads.length);
  }

  // Function to clear uploads after successful analysis
  function clearUploadsAfterSuccess() {
    uploads.forEach(upload => {
      URL.revokeObjectURL(upload.previewUrl);
    });
    uploads = [];
  }

  // Cleanup on destroy
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    uploads.forEach(upload => {
      URL.revokeObjectURL(upload.previewUrl);
    });
  });
</script>

<div class="multi-image-upload">
  <div 
    class="upload-zone {isDragging ? 'dragging' : ''}"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    role="button"
    tabindex="0"
    aria-label="Multi-image upload zone"
  >
    <div class="upload-content">
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <h3>{t('header.upload_multiple_images', 'ro')}</h3>
      <p>{t('message.drag_drop_images', 'ro')} <label class="browse-link">
        <input
          type="file"
          accept={acceptedTypes.join(',')}
          multiple
          on:change={handleFileInput}
          class="hidden-input"
        />
        {t('button.browse', 'ro')}
      </label></p>
      <small>{t('message.supports_format', 'ro')}: {acceptedTypes.map(t => t.split('/')[1]).join(', ')} ({t('message.max_size', 'ro')}: {maxFileSize / (1024 * 1024)}MB {t('message.each', 'ro')}, {t('message.up_to', 'ro')} {maxImages} {t('message.images', 'ro')})</small>
      {#if uploads.length > 0}
        <button class="clear-all-btn" on:click={clearAll}>{t('button.clear_all', 'ro')} ({uploads.length})</button>
      {/if}
    </div>
  </div>

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

  {#if uploads.length > 0}
    <div class="uploads-list">
      {#each uploads as upload (upload.id)}
        <div class="upload-item" in:scale={{ duration: 300, start: 0.8 }} animate:flip={{ duration: 300 }}>
          <div class="preview-container">
            <div class="preview-header">
              <span class="file-name">{upload.file.name}</span>
              <button class="remove-button" on:click={() => removeUpload(upload.id)} title="Remove image">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            
            <div class="preview-wrapper">
              <img src={upload.previewUrl} alt="Preview" class="preview-image" />
              
              {#if upload.isUploading}
                <div class="upload-overlay" in:fade={{ duration: 200 }}>
                  <div class="upload-progress">
                    <div class="progress-bar">
                      <div class="progress-fill" style="width: {upload.progress}%"></div>
                    </div>
                    <p>Analyzing...</p>
                  </div>
                </div>
              {:else if upload.isComplete}
                <div class="upload-overlay complete" in:fade={{ duration: 200 }}>
                  <div class="complete-indicator">
                    <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <p>Analysis Complete</p>
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/each}}
    </div>
    
    <div class="actions">
      <button 
        class="analyze-btn"
        on:click={analyzeAllImages}
        disabled={isAnalyzing || uploads.length === 0}
      >
        {isAnalyzing ? t('message.analyzing_images', 'ro') : t('button.analyze_images', 'ro').replace('{count}', uploads.length).replace('{plural}', uploads.length === 1 ? '' : 's'))}
      </button>
    </div>
  {/if}

  {#if synthesis}
    <div class="synthesis-results" in:fade={{ duration: 300 }}>
      <div class="synthesis-header">
        <h3>🏠 Property Overview</h3>
        <span class="room-count">{synthesis.total_rooms} room{synthesis.total_rooms === 1 ? '' : 's'} analyzed</span>
      </div>
      
      <div class="unified-description">
        {synthesis.unified_description}
      </div>
      
      {#if synthesis.room_breakdown && Object.keys(synthesis.room_breakdown).length > 0}
        <div class="room-breakdown">
          <h4>Room Summary:</h4>
          <div class="room-list">
            {#each Object.entries(synthesis.room_breakdown) as [roomType, count]}
              <div class="room-item">
                <span class="room-name">{roomType.replace('_', ' ').toLowerCase()}</span>
                <span class="room-count">{count}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      {#if synthesis.property_overview?.common_amenities?.length > 0}
        <div class="common-amenities">
          <h4>Notable Features:</h4>
          <div class="amenity-tags">
            {#each synthesis.property_overview.common_amenities.slice(0, 8) as amenity}
              <span class="amenity-tag">{amenity.replace('_', ' ')}</span>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .multi-image-upload {
    width: 100%;
    margin: 0 auto;
  }

  .upload-zone {
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafafa;
    margin-bottom: 1.5rem;
  }

  .upload-zone:hover {
    border-color: #9ca3af;
    background: #f5f5f5;
  }

  .upload-zone.dragging {
    border-color: #3b82f6;
    background: #eff6ff;
    transform: scale(1.02);
  }

  .upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }

  .upload-icon {
    width: 3rem;
    height: 3rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
  }

  .upload-zone:hover .upload-icon {
    color: #374151;
  }

  .upload-zone h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
  }

  .upload-zone p {
    margin: 0;
    color: #6b7280;
  }

  .browse-link {
    color: #3b82f6;
    cursor: pointer;
    text-decoration: underline;
  }

  .browse-link:hover {
    color: #2563eb;
  }

  .hidden-input {
    display: none;
  }

  .error-message {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #dc2626;
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

  .clear-all-btn {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }

  .clear-all-btn:hover {
    background: #dc2626;
  }

  .uploads-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .upload-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .preview-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1rem;
  }

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
  }

  .file-name {
    font-weight: 500;
    color: #374151;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .remove-button {
    background: none;
    border: none;
    cursor: pointer;
    color: #6b7280;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .remove-button:hover {
    background: #fee2e2;
    color: #dc2626;
  }

  .remove-button svg {
    width: 1.25rem;
    height: 1.25rem;
  }

  .preview-wrapper {
    position: relative;
    width: 100%;
    padding-bottom: 75%; /* 4:3 aspect ratio */
    overflow: hidden;
  }

  .preview-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .upload-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .upload-overlay.complete {
    background: rgba(34, 197, 94, 0.9);
  }

  .complete-indicator {
    text-align: center;
    color: white;
  }

  .check-icon {
    width: 3rem;
    height: 3rem;
    margin: 0 auto 0.5rem;
    stroke-width: 2;
  }

  .progress-bar {
    width: 200px;
    height: 4px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
    overflow: hidden;
    margin: 0.5rem auto;
  }

  .progress-fill {
    height: 100%;
    background: #3b82f6;
    transition: width 0.3s ease;
  }

  .actions {
    margin-top: 1.5rem;
    text-align: center;
  }

  .analyze-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .analyze-btn:hover:not(:disabled) {
    background: #2563eb;
  }

  .analyze-btn:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }

  .synthesis-results {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .synthesis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
  }

  .synthesis-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
  }

  .room-count {
    background: #3b82f6;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .unified-description {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    line-height: 1.6;
    color: #374151;
  }

  .room-breakdown {
    margin-bottom: 1rem;
  }

  .room-breakdown h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .room-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .room-item {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .room-name {
    font-size: 0.875rem;
    color: #475569;
    text-transform: capitalize;
  }

  .room-count {
    background: #3b82f6;
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    min-width: 1.5rem;
    text-align: center;
  }

  .common-amenities {
    margin-top: 1rem;
  }

  .common-amenities h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .amenity-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .amenity-tag {
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid #bae6fd;
  }
</style>