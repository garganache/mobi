<script lang="ts">
  import { onMount } from 'svelte';
  import MultiImageUpload from '$lib/components/MultiImageUpload.svelte';
  import PropertyAnalysisResults from '$lib/components/PropertyAnalysisResults.svelte';
  import { fade } from 'svelte/transition';

  let synthesis: any = null;
  let individualAnalyses: any[] = [];
  let showResults = false;

  function handleAnalysisComplete(event: CustomEvent) {
    synthesis = event.detail.synthesis;
    individualAnalyses = event.detail.individualAnalyses;
    showResults = true;
  }

  function handleUploadError(event: CustomEvent) {
    console.error('Upload error:', event.detail.error);
    alert(`Upload error: ${event.detail.error}`);
  }

  onMount(() => {
    // Auto-scroll to results when they appear
    if (showResults) {
      setTimeout(() => {
        const resultsElement = document.querySelector('.property-analysis-results');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }
  });
</script>

<div class="multi-image-demo">
  <div class="demo-header">
    <h1>Multi-Image Property Analysis</h1>
    <p class="demo-description">
      Upload multiple property images to get a unified analysis of your entire property. 
      The system will analyze each room individually and then synthesize a comprehensive overview.
    </p>
  </div>

  <div class="upload-section">
    <MultiImageUpload 
      on:analysisComplete={handleAnalysisComplete}
      on:uploadError={handleUploadError}
    />
  </div>

  {#if showResults && synthesis}
    <div class="results-section" in:fade={{ duration: 500 }}>
      <PropertyAnalysisResults 
        {synthesis} 
        {individualAnalyses}
        expanded={true}
      />
    </div>
  {/if}

  <div class="demo-features">
    <h2>How it works</h2>
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">📸</div>
        <h3>Upload Multiple Images</h3>
        <p>Drag and drop up to 10 property images at once. Supported formats: JPEG, PNG, WebP.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>AI Analysis</h3>
        <p>Each image is analyzed individually using advanced vision AI to identify rooms, features, and amenities.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🔗</div>
        <h3>Smart Synthesis</h3>
        <p>The system correlates all analyses to create a unified property description and room breakdown.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Detailed Results</h3>
        <p>Get both a comprehensive property overview and detailed individual room analyses.</p>
      </div>
    </div>
  </div>
</div>

<style>
  .multi-image-demo {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .demo-header {
    text-align: center;
    margin-bottom: 3rem;
  }

  .demo-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 1rem 0;
  }

  .demo-description {
    font-size: 1.125rem;
    color: #6b7280;
    line-height: 1.7;
    max-width: 600px;
    margin: 0 auto;
  }

  .upload-section {
    margin-bottom: 3rem;
  }

  .results-section {
    margin-bottom: 3rem;
  }

  .demo-features {
    margin-top: 4rem;
    padding-top: 3rem;
    border-top: 1px solid #e5e7eb;
  }

  .demo-features h2 {
    text-align: center;
    font-size: 2rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 2rem 0;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
  }

  .feature-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }

  .feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }

  .feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .feature-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 0.75rem 0;
  }

  .feature-card p {
    font-size: 0.95rem;
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .multi-image-demo {
      padding: 1rem;
    }

    .demo-header h1 {
      font-size: 2rem;
    }

    .demo-description {
      font-size: 1rem;
    }

    .features-grid {
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }
  }
</style>