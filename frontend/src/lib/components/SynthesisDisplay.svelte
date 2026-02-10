<script lang="ts">
  import { fade, slide } from 'svelte/transition';
  import { ChevronDown, ChevronUp, Home, Grid, CheckCircle } from 'lucide-svelte';

  export let synthesis: any = null;
  export let individualAnalyses: any[] = [];
  export let expanded: boolean = false;

  let showIndividualAnalyses = false;

  $: if (synthesis) {
    showIndividualAnalyses = false;
  }

  function formatRoomName(roomType: string): string {
    return roomType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  function formatAmenity(amenity: string): string {
    return amenity
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  function getRoomIcon(roomType: string): string {
    const icons: Record<string, string> = {
      'bedroom': '🛏️',
      'kitchen': '🍳',
      'living_room': '🛋️',
      'bathroom': '🚿',
      'hallway': '🚪',
      'dining_room': '🍽️',
      'office': '💼',
      'balcony': '🌿'
    };
    return icons[roomType] || '🏠';
  }
</script>

{#if synthesis}
  <div class="synthesis-container" in:fade={{ duration: 400 }}>
    <div class="synthesis-header">
      <div class="header-content">
        <div class="property-overview">
          <div class="overview-icon">
            <Home size={24} />
          </div>
          <div class="overview-text">
            <h3>Property Overview</h3>
            <p>{synthesis.total_rooms || 0} rooms analyzed</p>
          </div>
        </div>
        
        {#if synthesis.room_breakdown}
          <div class="room-summary">
            {#each Object.entries(synthesis.room_breakdown) as [roomType, count]}
              <div class="room-item">
                <span class="room-icon">{getRoomIcon(roomType)}</span>
                <span class="room-count">{count}</span>
                <span class="room-name">{formatRoomName(roomType)}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    {#if synthesis.unified_description}
      <div class="unified-description">
        <h4>Description</h4>
        <p>{synthesis.unified_description}</p>
      </div>
    {/if}

    {#if synthesis.amenities_by_room && Object.keys(synthesis.amenities_by_room).length > 0}
      <div class="amenities-section">
        <h4>Amenities by Room</h4>
        <div class="amenities-grid">
          {#each Object.entries(synthesis.amenities_by_room) as [roomName, amenities]}
            <div class="room-amenities">
              <h5>{formatRoomName(roomName)}</h5>
              <div class="amenity-list">
                {#each amenities as amenity}
                  <span class="amenity-tag">
                    <CheckCircle size={12} />
                    {formatAmenity(amenity)}
                  </span>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if individualAnalyses.length > 0}
      <div class="individual-analyses-toggle">
        <button 
          class="toggle-button"
          on:click={() => showIndividualAnalyses = !showIndividualAnalyses}
        >
          <Grid size={16} />
          <span>View Individual Analyses</span>
          {#if showIndividualAnalyses}
            <ChevronUp size={16} />
          {:else}
            <ChevronDown size={16} />
          {/if}
        </button>
      </div>

      {#if showIndividualAnalyses}
        <div class="individual-analyses" in:slide={{ duration: 300 }}>
          {#each individualAnalyses as analysis, index}
            <div class="analysis-card" in:fade={{ duration: 300, delay: index * 50 }}>
              <div class="analysis-header">
                <h5>Image {index + 1}</h5>
                {#if analysis.property_type}
                  <span class="property-type-tag">{formatRoomName(analysis.property_type)}</span>
                {/if}
              </div>
              
              {#if analysis.description}
                <p class="analysis-description">{analysis.description}</p>
              {/if}

              {#if analysis.rooms}
                <div class="analysis-rooms">
                  <strong>Rooms:</strong>
                  {#each Object.entries(analysis.rooms) as [roomType, count]}
                    <span class="room-badge">{formatRoomName(roomType)}: {count}</span>
                  {/each}
                </div>
              {/if}

              {#if analysis.amenities && analysis.amenities.length > 0}
                <div class="analysis-amenities">
                  <strong>Amenities:</strong>
                  <div class="amenity-tags">
                    {#each analysis.amenities as amenity}
                      <span class="amenity-tag">{formatAmenity(amenity)}</span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </div>
{/if}

<style>
  .synthesis-container {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .synthesis-header {
    margin-bottom: 1.5rem;
  }

  .property-overview {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .overview-icon {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    padding: 0.75rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .overview-text h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 700;
    color: #1f2937;
  }

  .overview-text p {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
  }

  .room-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .room-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  .room-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .room-count {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f2937;
  }

  .room-name {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.25rem;
  }

  .unified-description {
    background: #f9fafb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .unified-description h4 {
    margin: 0 0 0.5rem 0;
    color: #374151;
    font-size: 1rem;
  }

  .unified-description p {
    margin: 0;
    color: #4b5563;
    line-height: 1.5;
  }

  .amenities-section h4 {
    margin: 0 0 1rem 0;
    color: #374151;
    font-size: 1rem;
  }

  .amenities-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .room-amenities {
    background: #f9fafb;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #e5e7eb;
  }

  .room-amenities h5 {
    margin: 0 0 0.75rem 0;
    color: #374151;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .amenity-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .amenity-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .individual-analyses-toggle {
    margin-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
    padding-top: 1rem;
  }

  .toggle-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #f3f4f6;
    color: #374151;
    border: 1px solid #d1d5db;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-button:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
  }

  .individual-analyses {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
  }

  .analysis-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
  }

  .analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .analysis-header h5 {
    margin: 0;
    color: #374151;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .property-type-tag {
    background: #dbeafe;
    color: #1d4ed8;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .analysis-description {
    color: #4b5563;
    font-size: 0.875rem;
    line-height: 1.4;
    margin: 0 0 0.75rem 0;
  }

  .analysis-rooms {
    margin-bottom: 0.75rem;
  }

  .analysis-rooms strong {
    color: #374151;
    font-size: 0.875rem;
  }

  .room-badge {
    display: inline-block;
    background: #e5e7eb;
    color: #374151;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
  }

  .analysis-amenities strong {
    color: #374151;
    font-size: 0.875rem;
    display: block;
    margin-bottom: 0.5rem;
  }

  .amenity-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .room-summary {
      grid-template-columns: repeat(2, 1fr);
    }

    .amenities-grid {
      grid-template-columns: 1fr;
    }

    .individual-analyses {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 480px) {
    .room-summary {
      grid-template-columns: 1fr;
    }

    .synthesis-container {
      padding: 1rem;
    }
  }
</style>