# TASK-043: Update Synthesis Display to Use Romanian

**Story:** STORY-008 (Romanian Localization)
**Status:** todo
**Priority:** medium
**Assigned:** -
**Effort:** 2 hours
**Depends on:** TASK-037, TASK-042

## Objective

Ensure the synthesis display component (property overview section) shows all text in Romanian.

## Files to Update

### 1. SynthesisDisplay.svelte

**File:** `frontend/src/lib/components/SynthesisDisplay.svelte`

**Current Issues:**
- "Property Overview" - needs translation
- "{count} images analyzed" - needs translation
- "Rooms detected in images:" - needs translation
- "Description" - needs translation
- "Amenities by Room" - needs translation
- Room names - need translation
- Amenity names - need translation

**Updated Implementation:**

```svelte
<script lang="ts">
  import { fade, slide } from 'svelte/transition';
  import { ChevronDown, ChevronUp, Home, Grid, CheckCircle } from 'lucide-svelte';
  import { t, getRoomLabel, getAmenityLabel } from '$lib/i18n';

  export let synthesis: any = null;
  export let individualAnalyses: any[] = [];
  export let expanded: boolean = false;

  let showIndividualAnalyses = true;

  $: if (synthesis) {
    showIndividualAnalyses = true;
  }

  function formatRoomName(roomType: string): string {
    return getRoomLabel(roomType);
  }

  function formatAmenity(amenity: string): string {
    return getAmenityLabel(amenity);
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
      'balcony': '🌿',
      'garage': '🚗',
      'laundry_room': '🧺',
      'gym': '🏋️',
      'patio': '🪴',
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
            <h3>{t('header.property_overview')}</h3>
            <p>
              {individualAnalyses?.length || 0} 
              {individualAnalyses?.length === 1 
                ? t('message.image_analyzed') 
                : t('message.images_analyzed')}
            </p>
          </div>
        </div>
        
        {#if synthesis.room_breakdown}
          <div class="room-summary">
            <p class="rooms-detected-label">{t('message.rooms_detected')}</p>
            {#each Object.entries(synthesis.room_breakdown) as [roomType, count]}
              <div class="room-item">
                <span class="room-icon">{getRoomIcon(roomType)}</span>
                <span class="room-name">{formatRoomName(roomType)}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    {#if synthesis.unified_description}
      <div class="unified-description">
        <h4>{t('header.description')}</h4>
        <p>{synthesis.unified_description}</p>
      </div>
    {/if}

    {#if synthesis.amenities_by_room && Object.keys(synthesis.amenities_by_room).length > 0}
      <div class="amenities-section">
        <h4>{t('header.amenities_by_room')}</h4>
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

    <!-- Individual analyses section -->
    {#if showIndividualAnalyses && individualAnalyses?.length > 0}
      <div class="individual-analyses">
        <button
          class="toggle-analyses"
          on:click={() => expanded = !expanded}
        >
          <span>{t('header.individual_analyses')}</span>
          {#if expanded}
            <ChevronUp size={20} />
          {:else}
            <ChevronDown size={20} />
          {/if}
        </button>

        {#if expanded}
          <div class="analyses-list" transition:slide>
            {#each individualAnalyses as analysis, index}
              <div class="analysis-item">
                <div class="analysis-header">
                  <span class="analysis-number">{t('label.image')} {index + 1}</span>
                </div>
                
                {#if analysis.rooms && Object.keys(analysis.rooms).length > 0}
                  <div class="analysis-rooms">
                    <strong>{t('label.rooms')}:</strong>
                    {#each Object.entries(analysis.rooms) as [room, count]}
                      <span class="room-badge">
                        {getRoomIcon(room)} {formatRoomName(room)}
                      </span>
                    {/each}
                  </div>
                {/if}

                {#if analysis.amenities && analysis.amenities.length > 0}
                  <div class="analysis-amenities">
                    <strong>{t('label.amenities')}:</strong>
                    {#each analysis.amenities as amenity}
                      <span class="amenity-badge">{formatAmenity(amenity)}</span>
                    {/each}
                  </div>
                {/if}

                {#if analysis.description}
                  <p class="analysis-description">{analysis.description}</p>
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
  /* ... existing styles ... */
</style>
```

### 2. Add Missing Translations

**File:** `frontend/src/lib/i18n/index.ts`

```typescript
export const translations = {
  ro: {
    // ... existing translations ...
    
    // Headers
    'header.property_overview': 'Prezentare Proprietate',
    'header.description': 'Descriere',
    'header.amenities_by_room': 'Facilități pe Cameră',
    'header.individual_analyses': 'Analize Individuale',
    
    // Messages
    'message.image_analyzed': 'imagine analizată',
    'message.images_analyzed': 'imagini analizate',
    'message.rooms_detected': 'Camere detectate în imagini:',
    
    // Labels
    'label.image': 'Imagine',
    'label.rooms': 'Camere',
    'label.amenities': 'Facilități',
  }
};
```

### 3. Update VisionAnalysisDisplay Component (if used)

**File:** `frontend/src/lib/components/VisionAnalysisDisplay.svelte`

Apply same translation approach:

```svelte
<script>
  import { t, getRoomLabel, getAmenityLabel } from '$lib/i18n';
</script>

<div class="vision-analysis">
  <h3>{t('header.ai_analysis')}</h3>
  
  {#if analysis.property_type}
    <p>
      <strong>{t('field.property_type')}:</strong> 
      {getPropertyTypeLabel(analysis.property_type)}
    </p>
  {/if}
  
  {#if analysis.rooms}
    <p>
      <strong>{t('label.rooms')}:</strong>
      {#each Object.entries(analysis.rooms) as [room, count]}
        {formatRoomName(room)}
      {/each}
    </p>
  {/if}
  
  <!-- ... rest of component ... -->
</div>
```

## Acceptance Criteria

- [ ] "Property Overview" → "Prezentare Proprietate"
- [ ] "X images analyzed" → "X imagini analizate"
- [ ] "Rooms detected in images:" → "Camere detectate în imagini:"
- [ ] "Description" → "Descriere"
- [ ] "Amenities by Room" → "Facilități pe Cameră"
- [ ] All room names in Romanian
- [ ] All amenity names in Romanian
- [ ] Individual analyses section in Romanian
- [ ] No English text visible in synthesis display
- [ ] Singular/plural forms correct ("1 imagine" vs "2 imagini")

## Testing

### Manual Test

1. Upload images and wait for analysis
2. Check synthesis display:
   - Header: "Prezentare Proprietate" ✓
   - Count: "2 imagini analizate" ✓
   - Label: "Camere detectate în imagini:" ✓
   - Rooms: "Dormitor", "Bucătărie" ✓
   - Description section header: "Descriere" ✓
   - Amenities section: "Facilități pe Cameră" ✓

### Automated Test

```typescript
test('SynthesisDisplay shows Romanian text', async () => {
  const synthesis = {
    room_breakdown: {
      'bedroom': 1,
      'kitchen': 1
    },
    unified_description: 'Acest apartament...',
    amenities_by_room: {
      'kitchen': ['granite_counters']
    }
  };
  
  const individualAnalyses = [
    { rooms: { bedroom: 1 }, amenities: ['hardwood_floors'] }
  ];
  
  const { getByText } = render(SynthesisDisplay, {
    synthesis,
    individualAnalyses
  });
  
  expect(getByText('Prezentare Proprietate')).toBeInTheDocument();
  expect(getByText('1 imagine analizată')).toBeInTheDocument();
  expect(getByText('Camere detectate în imagini:')).toBeInTheDocument();
  expect(getByText('Dormitor')).toBeInTheDocument();
  expect(getByText('Bucătărie')).toBeInTheDocument();
  expect(getByText('Blat de Granit')).toBeInTheDocument();
});
```

## Notes

- Pay attention to singular/plural forms in Romanian
- "1 imagine analizată" (singular)
- "2 imagini analizate" (plural)
- Ensure proper Romanian grammar throughout
- Test with various room/amenity combinations
