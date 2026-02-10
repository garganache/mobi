<script lang="ts">
  import { fade, slide } from 'svelte/transition';
  import VisionAnalysisDisplay from './VisionAnalysisDisplay.svelte';

  export let synthesis: any;
  export let individualAnalyses: any[] = [];
  export let expanded = false;

  let showIndividualAnalyses = false;

  $: if (expanded) {
    showIndividualAnalyses = true;
  }

  function toggleIndividualAnalyses() {
    showIndividualAnalyses = !showIndividualAnalyses;
  }
</script>

{#if synthesis}
  <div class="property-analysis-results">
    <!-- Synthesis Section - Always Visible -->
    <div class="synthesis-section">
      <div class="synthesis-header">
        <div class="synthesis-title">
          <span class="property-icon">🏠</span>
          <h3>Property Analysis</h3>
          {#if synthesis.layout_type === 'open_concept'}
            <span class="layout-badge open-concept">Open Concept</span>
          {/if}
        </div>
        <div class="synthesis-meta">
          <span class="room-badge">{synthesis.total_rooms} room{synthesis.total_rooms === 1 ? '' : 's'}</span>
          <span class="confidence-badge">{synthesis.property_overview?.condition || 'analyzed'}</span>
        </div>
      </div>
      
      <div class="unified-description">
        {synthesis.unified_description}
      </div>
      
      {#if synthesis.room_breakdown && Object.keys(synthesis.room_breakdown).length > 0}
        <div class="room-summary">
          <h4>Room Breakdown:</h4>
          <div class="room-grid">
            {#each Object.entries(synthesis.room_breakdown) as [roomType, count]}
              <div class="room-card">
                <div class="room-icon">🚪</div>
                <div class="room-info">
                  <div class="room-name">{roomType.replace('_', ' ').toLowerCase()}</div>
                  <div class="room-count">{count}</div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      {#if synthesis.property_overview?.common_amenities?.length > 0}
        <div class="amenities-section">
          <h4>Key Features:</h4>
          <div class="amenity-chips">
            {#each synthesis.property_overview.common_amenities.slice(0, 6) as amenity}
              <span class="amenity-chip">{amenity.replace('_', ' ')}</span>
            {/each}
            {#if synthesis.property_overview.common_amenities.length > 6}
              <span class="amenity-more">+{synthesis.property_overview.common_amenities.length - 6} more</span>
            {/if}
          </div>
        </div>
      {/if}
      
      {#if synthesis.exterior_features && synthesis.exterior_features.length > 0}
        <div class="exterior-features-section">
          <h4>Exterior Features:</h4>
          <div class="exterior-chips">
            {#each synthesis.exterior_features as feature}
              <span class="exterior-chip">{feature}</span>
            {/each}
          </div>
        </div>
      {/if}
      
      {#if synthesis.property_overview}
        <div class="property-insights">
          <div class="insight-item">
            <span class="insight-label">Property Type:</span>
            <span class="insight-value">{synthesis.property_overview.property_type || 'unknown'}</span>
          </div>
          <div class="insight-item">
            <span class="insight-label">Style:</span>
            <span class="insight-value">{synthesis.property_overview.style || 'unknown'}</span>
          </div>
          <div class="insight-item">
            <span class="insight-label">Condition:</span>
            <span class="insight-value">{synthesis.property_overview.condition || 'unknown'}</span>
          </div>
        </div>
      {/if}
    </div>

    <!-- Individual Analyses - Collapsible -->
    {#if individualAnalyses.length > 0}
      <div class="individual-analyses-section">
        <button 
          class="toggle-button"
          on:click={toggleIndividualAnalyses}
          aria-expanded={showIndividualAnalyses}
        >
          <span class="toggle-icon">
            <svg 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor"
              class:rotated={showIndividualAnalyses}
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </span>
          <span>View Individual Room Analyses ({individualAnalyses.length})</span>
        </button>
        
        {#if showIndividualAnalyses}
          <div class="individual-analyses" in:slide={{ duration: 300 }} out:slide={{ duration: 200 }}>
            {#each individualAnalyses as analysis, index}
              <div class="individual-analysis-card" in:fade={{ duration: 300, delay: index * 50 }}>
                <div class="analysis-header">
                  <div class="analysis-title">
                    <span class="image-number">Image {index + 1}</span>
                    {#if analysis.property_type}
                      <span class="property-type">{analysis.property_type}</span>
                    {/if}
                  </div>
                  {#if analysis.condition}
                    <span class="condition-badge {analysis.condition}">{analysis.condition}</span>
                  {/if}
                </div>
                
                {#if analysis.description}
                  <p class="analysis-description">{analysis.description}</p>
                {/if}
                
                {#if analysis.rooms && Object.keys(analysis.rooms).length > 0}
                  <div class="rooms-detected">
                    <strong>Rooms:</strong>
                    {Object.entries(analysis.rooms)
                      .map(([type, count]) => `${count} ${type.replace('_', ' ')}${count > 1 ? 's' : ''}`)
                      .join(', ')}
                  </div>
                {/if}
                
                {#if analysis.amenities && analysis.amenities.length > 0}
                  <div class="amenities-detected">
                    <strong>Features:</strong>
                    <div class="amenity-tags">
                      {#each analysis.amenities.slice(0, 6) as amenity}
                        <span class="amenity-tag">{amenity.replace('_', ' ')}</span>
                      {/each}
                      {#if analysis.amenities.length > 6}
                        <span class="more-amenities">+{analysis.amenities.length - 6}</span>
                      {/if}
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
{/if}

<style>
  .property-analysis-results {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  }

  .synthesis-section {
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  }

  .synthesis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .synthesis-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .property-icon {
    font-size: 1.5rem;
  }

  .synthesis-title h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f2937;
  }

  .synthesis-meta {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .room-badge {
    background: #3b82f6;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .confidence-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .unified-description {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    line-height: 1.6;
    color: #374151;
    font-size: 0.95rem;
  }

  .room-summary {
    margin-bottom: 1rem;
  }

  .room-summary h4 {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .room-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
  }

  .room-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
  }

  .room-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
  }

  .room-icon {
    font-size: 1.25rem;
  }

  .room-info {
    flex: 1;
  }

  .room-name {
    font-size: 0.875rem;
    color: #475569;
    text-transform: capitalize;
  }

  .room-count {
    font-size: 1.125rem;
    font-weight: 700;
    color: #1f2937;
  }

  .amenities-section {
    margin-bottom: 1rem;
  }

  .amenities-section h4 {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .amenity-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .amenity-chip {
    background: #dbeafe;
    color: #1e40af;
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid #bfdbfe;
    text-transform: capitalize;
  }

  .amenity-more {
    background: #f3f4f6;
    color: #6b7280;
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid #e5e7eb;
  }

  .exterior-features-section {
    margin-bottom: 1rem;
  }

  .exterior-features-section h4 {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
  }

  .exterior-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .exterior-chip {
    background: #d1fae5;
    color: #065f46;
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    border: 1px solid #a7f3d0;
    text-transform: capitalize;
  }

  .layout-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .layout-badge.open-concept {
    background: #dbeafe;
    color: #1e40af;
    border: 1px solid #bfdbfe;
  }

  .property-insights {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  .insight-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .insight-label {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .insight-value {
    font-size: 0.875rem;
    color: #374151;
    font-weight: 600;
    text-transform: capitalize;
  }

  .individual-analyses-section {
    border-top: 1px solid #e5e7eb;
  }

  .toggle-button {
    width: 100%;
    background: #f9fafb;
    border: none;
    border-top: 1px solid #e5e7eb;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    transition: all 0.2s;
  }

  .toggle-button:hover {
    background: #f3f4f6;
  }

  .toggle-icon svg {
    width: 1.25rem;
    height: 1.25rem;
    transition: transform 0.2s;
  }

  .toggle-icon svg.rotated {
    transform: rotate(180deg);
  }

  .individual-analyses {
    padding: 0 1.5rem 1.5rem;
    background: #f9fafb;
  }

  .individual-analysis-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .individual-analysis-card:last-child {
    margin-bottom: 0;
  }

  .analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .analysis-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .image-number {
    background: #3b82f6;
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .property-type {
    background: #f3f4f6;
    color: #6b7280;
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: capitalize;
  }

  .condition-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
  }

  .condition-badge.excellent {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
  }

  .condition-badge.good {
    background: #dbeafe;
    color: #1e40af;
    border: 1px solid #bfdbfe;
  }

  .condition-badge.fair {
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
  }

  .condition-badge.needs_work {
    background: #fee2e2;
    color: #dc2626;
    border: 1px solid #fca5a5;
  }

  .analysis-description {
    margin: 0 0 0.75rem 0;
    font-size: 0.875rem;
    line-height: 1.5;
    color: #374151;
  }

  .rooms-detected {
    margin-bottom: 0.75rem;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .rooms-detected strong {
    color: #374151;
  }

  .amenities-detected {
    margin-bottom: 0;
  }

  .amenities-detected strong {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: #374151;
  }

  .amenity-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
  }

  .amenity-tag {
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid #bae6fd;
    text-transform: capitalize;
  }

  .more-amenities {
    background: #f3f4f6;
    color: #6b7280;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid #e5e7eb;
  }
</style>