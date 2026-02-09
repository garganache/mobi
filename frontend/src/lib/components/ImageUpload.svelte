<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';

  export let maxFileSize = 10 * 1024 * 1024; // 10MB
  export let acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  export let uploadEndpoint = '/api/analyze-step';
  
  let file: File | null = null;
  let previewUrl: string | null = null;
  let isDragging = false;
  let isUploading = false;
  let error: string | null = null;
  let progress = 0;

  const dispatch = createEventDispatcher<{
    uploadStart: void;
    uploadSuccess: { response: any };
    uploadError: { error: string };
    fileSelected: { file: File };
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

  function handleFileSelect(selectedFile: File) {
    error = null;
    const validationError = validateFile(selectedFile);
    
    if (validationError) {
      error = validationError;
      return;
    }

    file = selectedFile;
    dispatch('fileSelected', { file: selectedFile });
    
    // Create preview
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    previewUrl = URL.createObjectURL(selectedFile);
    
    // Auto-upload after selection
    uploadFile(selectedFile);
  }

  async function uploadFile(fileToUpload: File) {
    isUploading = true;
    error = null;
    progress = 0;
    
    dispatch('uploadStart');

    try {
      // Convert file to base64 for the API
      const base64 = await fileToBase64(fileToUpload);
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        progress = Math.min(progress + 10, 90);
      }, 200);

      const response = await fetch(uploadEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_type: 'image',
          new_input: base64,
          current_data: {}
        })
      });

      clearInterval(progressInterval);
      progress = 100;

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      dispatch('uploadSuccess', { response: result });
      
      // Reset after successful upload
      setTimeout(() => {
        isUploading = false;
        progress = 0;
      }, 500);

    } catch (err) {
      clearInterval(progressInterval);
      isUploading = false;
      progress = 0;
      error = err instanceof Error ? err.message : 'Upload failed';
      dispatch('uploadError', { error: error || 'Unknown error' });
    }
  }

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove the data:image/... prefix to get just the base64 data
        const base64String = (reader.result as string).split(',')[1];
        resolve(base64String);
      };
      reader.onerror = reject;
    });
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging = false;
    
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
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
      handleFileSelect(files[0]);
    }
  }

  function clearFile() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
    file = null;
    error = null;
    progress = 0;
    isUploading = false;
  }

  // Cleanup on destroy
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  });
</script>

<div class="image-upload">
  {#if !file && !isUploading}
    <div 
      class="upload-zone {isDragging ? 'dragging' : ''}"
      on:drop={handleDrop}
      on:dragover={handleDragOver}
      on:dragleave={handleDragLeave}
      in:fade={{ duration: 300 }}
      role="button"
      tabindex="0"
      aria-label="Image upload zone"
    >
      <div class="upload-content">
        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <h3>Upload Property Image</h3>
        <p>Drag and drop your image here, or <label class="browse-link">
          <input
            type="file"
            accept={acceptedTypes.join(',')}
            on:change={handleFileInput}
            class="hidden-input"
          />
          browse
        </label></p>
        <small>Supports: {acceptedTypes.map(t => t.split('/')[1]).join(', ')} (max {maxFileSize / (1024 * 1024)}MB)</small>
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

  {#if file && previewUrl}
    <div class="preview-container" in:scale={{ duration: 300, start: 0.8 }}>
      <div class="preview-header">
        <span class="file-name">{file.name}</span>
        <button class="remove-button" on:click={clearFile} title="Remove image">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
      
      <div class="preview-wrapper">
        <img src={previewUrl} alt="Preview" class="preview-image" />
        
        {#if isUploading}
          <div class="upload-overlay" in:fade={{ duration: 200 }}>
            <div class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
              </div>
              <p>Uploading and analyzing...</p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .image-upload {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
  }

  .upload-zone {
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafafa;
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

  .preview-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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

  .upload-progress {
    text-align: center;
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
</style>