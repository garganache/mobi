<script lang="ts">
  import { fade, slide } from 'svelte/transition';

  export let analysis: any = null;
  export let compact = false;

  let isExpanded = !compact;

  function toggleExpanded() {
    isExpanded = !isExpanded;
  }

  function formatRooms(rooms: any): string {
    if (!rooms) return 'N/A';
    return Object.entries(rooms)
      .map(([type, count]) => `${count} ${type}${count > 1 ? 's' : ''}`)
      .join(', ');
  }

  function formatList(items: any): string {
    if (!items) return 'N/A';
    if (Array.isArray(items)) {
      return items.length > 0 ? items.join(', ') : 'None detected';
    }
    return 'N/A';
  }
</script>

{#if analysis}
  <div class="vision-analysis" in:fade={{ duration: 300 }}>
    <div class="header" on:click={compact ? toggleExpanded : null} class:clickable={compact}>
      <div class="title">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3>AI Analysis Results</h3>
      </div>
      {#if compact}
        <button class="toggle-btn" aria-label={isExpanded ? 'Collapse' : 'Expand'}>
          <svg class="chevron" class:rotated={isExpanded} viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      {/if}
    </div>

    {#if isExpanded}
      <div class="content" transition:slide={{ duration: 200 }}>
        {#if analysis.description}
          <div class="section description-section">
            <h4>Property Description</h4>
            <p class="description">{analysis.description}</p>
          </div>
        {/if}

        <div class="details-grid">
          {#if analysis.property_type}
            <div class="detail-item">
              <span class="detail-label">Property Type:</span>
              <span class="detail-value property-type">{analysis.property_type}</span>
            </div>
          {/if}

          {#if analysis.style}
            <div class="detail-item">
              <span class="detail-label">Style:</span>
              <span class="detail-value">{analysis.style}</span>
            </div>
          {/if}

          {#if analysis.condition}
            <div class="detail-item">
              <span class="detail-label">Condition:</span>
              <span class="detail-value condition-{analysis.condition}">
                {analysis.condition}
              </span>
            </div>
          {/if}

          {#if analysis.rooms}
            <div class="detail-item full-width">
              <span class="detail-label">Rooms:</span>
              <span class="detail-value">{formatRooms(analysis.rooms)}</span>
            </div>
          {/if}

          {#if analysis.amenities}
            <div class="detail-item full-width">
              <span class="detail-label">Amenities:</span>
              <span class="detail-value">{formatList(analysis.amenities)}</span>
            </div>
          {/if}

          {#if analysis.materials}
            <div class="detail-item full-width">
              <span class="detail-label">Materials & Finishes:</span>
              <span class="detail-value">{formatList(analysis.materials)}</span>
            </div>
          {/if}
        </div>

        {#if analysis.confidence_scores}
          <div class="confidence-section">
            <h4>Confidence Scores</h4>
            <div class="confidence-grid">
              {#each Object.entries(analysis.confidence_scores) as [key, value]}
                <div class="confidence-item">
                  <span class="confidence-label">{key.replace(/_/g, ' ')}:</span>
                  <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {value * 100}%"></div>
                  </div>
                  <span class="confidence-value">{Math.round(value * 100)}%</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        {#if analysis.analysis_id}
          <div class="footer">
            <small class="analysis-id">Analysis ID: {analysis.analysis_id}</small>
          </div>
        {/if}
      </div>
    {/if}
  </div>
{/if}

<style>
  .vision-analysis {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    margin: 1rem 0;
  }

  .header {
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header.clickable {
    cursor: pointer;
  }

  .header.clickable:hover {
    background: linear-gradient(135deg, #5568d3 0%, #6a3f8e 100%);
  }

  .title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .icon {
    width: 1.5rem;
    height: 1.5rem;
    stroke-width: 2.5;
  }

  h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
  }

  .toggle-btn {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .chevron {
    width: 1.5rem;
    height: 1.5rem;
    transition: transform 0.2s ease;
  }

  .chevron.rotated {
    transform: rotate(180deg);
  }

  .content {
    padding: 1.5rem;
  }

  .section {
    margin-bottom: 1.5rem;
  }

  .section:last-child {
    margin-bottom: 0;
  }

  h4 {
    margin: 0 0 0.75rem 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .description-section {
    background: #f9fafb;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
  }

  .description {
    margin: 0;
    color: #374151;
    line-height: 1.6;
    font-size: 0.95rem;
  }

  .details-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .detail-item.full-width {
    grid-column: 1 / -1;
  }

  .detail-label {
    font-size: 0.875rem;
    color: #6b7280;
    font-weight: 500;
  }

  .detail-value {
    font-size: 1rem;
    color: #1f2937;
    font-weight: 500;
  }

  .property-type {
    text-transform: capitalize;
    color: #667eea;
  }

  .condition-excellent {
    color: #10b981;
  }

  .condition-good {
    color: #3b82f6;
  }

  .condition-fair {
    color: #f59e0b;
  }

  .condition-needs_work {
    color: #ef4444;
  }

  .confidence-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
  }

  .confidence-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .confidence-item {
    display: grid;
    grid-template-columns: 120px 1fr 50px;
    align-items: center;
    gap: 0.75rem;
  }

  .confidence-label {
    font-size: 0.875rem;
    color: #6b7280;
    text-transform: capitalize;
  }

  .confidence-bar {
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
  }

  .confidence-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transition: width 0.3s ease;
  }

  .confidence-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    text-align: right;
  }

  .footer {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  .analysis-id {
    color: #9ca3af;
    font-size: 0.75rem;
  }
</style>
