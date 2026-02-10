<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { t } from '../i18n';
  import VisionAnalysisDisplay from './VisionAnalysisDisplay.svelte';

  export let maxFileSize = 10 * 1024 * 1024; // 10MB
  export let acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  export let uploadEndpoint = '/api/analyze-step';
  export let multiple = true; // Support multiple images
  export let batchMode = false; // Use batch API for multiple images
  
  interface ImageUpload {
    id: string;
    file: File;
    previewUrl: string;
    isUploading: boolean;
    progress: number;
    error: string | null;
    analysis: any | null;
  }

  let uploads: ImageUpload[] = [];
  let isDragging = false;
  let error: string | null = null;
  let isBatchUploading = false;
  let batchUploadProgress = 0;

  const dispatch = createEventDispatcher<{
    uploadStart: { id: string; batch?: boolean };
    uploadSuccess: { id: string; response: any; imageUrl?: string; batch?: boolean; synthesis?: any };
    uploadError: { id: string; error: string; batch?: boolean };
    fileSelected: { files: File[] };
    allUploadsComplete: { analyses: any[] };
    batchUploadStart: { fileCount: number };
    batchUploadSuccess: { synthesis: any; individualAnalyses: any[]; imageUrls: string[] };
    batchUploadError: { error: string };
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
    
    dispatch('fileSelected', { files: validFiles });
    
    // Create upload entries
    const newUploads: ImageUpload[] = validFiles.map(file => ({
      id: generateId(),
      file,
      previewUrl: URL.createObjectURL(file),
      isUploading: true,
      progress: 0,
      error: null,
      analysis: null,
    }));
    
    uploads = [...uploads, ...newUploads];
    
    // Use batch API if enabled and multiple files are selected
    if (batchMode && validFiles.length > 1) {
      uploadBatchFiles(validFiles);
    } else {
      // Auto-upload files individually
      newUploads.forEach(upload => uploadFile(upload));
    }
  }

  async function uploadFile(upload: ImageUpload) {
    dispatch('uploadStart', { id: upload.id });

    const progressInterval = setInterval(() => {
      uploads = uploads.map(u => 
        u.id === upload.id 
          ? { ...u, progress: Math.min(u.progress + 10, 90) }
          : u
      );
    }, 200);

    try {
      // Convert file to base64 for the API
      const base64 = await fileToBase64(upload.file);

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

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      
      // Update upload with result
      uploads = uploads.map(u => 
        u.id === upload.id 
          ? { 
              ...u, 
              isUploading: false, 
              progress: 100,
              analysis: result.vision_analysis || null,
              error: null
            }
          : u
      );
      
      dispatch('uploadSuccess', { 
        id: upload.id, 
        response: result,
        imageUrl: upload.previewUrl  // Include image URL for tracking
      });
      
      // Check if all uploads are complete
      const allComplete = uploads.every(u => !u.isUploading);
      if (allComplete) {
        const analyses = uploads.map(u => u.analysis).filter(a => a !== null);
        dispatch('allUploadsComplete', { analyses });
      }

    } catch (err) {
      clearInterval(progressInterval);
      const errorMsg = err instanceof Error ? err.message : 'Upload failed';
      
      uploads = uploads.map(u => 
        u.id === upload.id 
          ? { ...u, isUploading: false, progress: 0, error: errorMsg }
          : u
      );
      
      dispatch('uploadError', { id: upload.id, error: errorMsg });
    }
  }

  async function uploadBatchFiles(files: File[]) {
    isBatchUploading = true;
    batchUploadProgress = 0;
    dispatch('batchUploadStart', { fileCount: files.length });

    // Simulate progress
    const progressInterval = setInterval(() => {
      batchUploadProgress = Math.min(batchUploadProgress + 10, 90);
    }, 300);

    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      const response = await fetch('/api/analyze-batch', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Batch upload failed' }));
        throw new Error(errorData.detail || 'Batch upload failed');
      }

      const result = await response.json();
      
      clearInterval(progressInterval);
      batchUploadProgress = 100;
      
      // Create upload entries for display and collect image URLs
      const newUploads: ImageUpload[] = files.map((file, index) => ({
        id: generateId(),
        file,
        previewUrl: URL.createObjectURL(file),
        isUploading: false,
        progress: 100,
        error: null,
        analysis: result.individual_analyses[index] || null,
      }));
      
      uploads = [...uploads, ...newUploads];
      
      // Extract image URLs for parent component
      const imageUrls = newUploads.map(u => u.previewUrl);
      
      dispatch('batchUploadSuccess', { 
        synthesis: result.synthesis,
        individualAnalyses: result.individual_analyses,
        imageUrls: imageUrls
      });

    } catch (err) {
      clearInterval(progressInterval);
      const errorMsg = err instanceof Error ? err.message : 'Batch upload failed';
      dispatch('batchUploadError', { error: errorMsg });
      error = errorMsg;
    } finally {
      setTimeout(() => {
        isBatchUploading = false;
        batchUploadProgress = 0;
      }, 500);
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
      const fileArray = Array.from(files);
      handleFileSelect(multiple ? fileArray : [fileArray[0]]);
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
      handleFileSelect(multiple ? fileArray : [fileArray[0]]);
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
  }

  function clearAll() {
    uploads.forEach(upload => {
      URL.revokeObjectURL(upload.previewUrl);
    });
    uploads = [];
    error = null;
  }

  // Cleanup on destroy
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    uploads.forEach(upload => {
      URL.revokeObjectURL(upload.previewUrl);
    });
  });
</script>

<div class="image-upload">
  <div 
    class="upload-zone {isDragging ? 'dragging' : ''}"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    role="button"
    tabindex="0"
    aria-label="Image upload zone"
  >
    <div class="upload-content">
      <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <h3>{t('header.upload_property_images', 'ro')}</h3>
      <p>{t('message.drag_drop_or', 'ro')} <label class="browse-link">
        <input
          type="file"
          accept={acceptedTypes.join(',')}
          {multiple}
          on:change={handleFileInput}
          class="hidden-input"
        />
        {t('button.browse', 'ro')}
      </label></p>
      <small>{t('message.supports_format', 'ro')}: {acceptedTypes.map(t => t.split('/')[1]).join(', ')} ({t('message.max_size', 'ro')}: {maxFileSize / (1024 * 1024)}MB{multiple ? ' ' + t('message.each', 'ro') : ''})</small>
      {#if multiple && uploads.length > 0}
        <button class="clear-all-btn" on:click={clearAll}>{t('button.clear_all', 'ro')} ({uploads.length})</button>
      {/if}
    </div>
  </div>

  {#if isBatchUploading}
    <div class="batch-upload-progress" in:fade={{ duration: 300 }}>
      <div class="progress-header">
        <svg class="progress-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <span>{t('message.analyzing_images', 'ro')}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: {batchUploadProgress}%"></div>
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
                    <p>{t('message.processing', 'ro')}</p>
                  </div>
                </div>
              {/if}
            </div>

            {#if upload.error}
              <div class="upload-error">
                <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {upload.error}
              </div>
            {/if}
          </div>

          {#if upload.analysis}
            <VisionAnalysisDisplay analysis={upload.analysis} compact={true} />
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .image-upload {
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

  .upload-error {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 6px;
    padding: 0.75rem;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #dc2626;
    font-size: 0.875rem;
  }

  .upload-error .error-icon {
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
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

  /* Batch upload progress styles */
  .batch-upload-progress {
    background: #eff6ff;
    border: 1px solid #3b82f6;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
  }

  .progress-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    color: #1e40af;
    font-weight: 500;
  }

  .progress-icon {
    width: 1.5rem;
    height: 1.5rem;
    color: #3b82f6;
  }

  .batch-upload-progress .progress-bar {
    width: 100%;
    max-width: 300px;
    height: 8px;
    background: #dbeafe;
    border-radius: 4px;
    overflow: hidden;
    margin: 0 auto;
  }

  .batch-upload-progress .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
    transition: width 0.5s ease;
  }
</style>