# TASK-045: Create Listings List View Page

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Complete  
**Priority:** High  
**Estimated:** 45 min  
**Completed:** 2026-02-11

## Objective

Create a page that displays all saved property listings in a simple card grid.

## Requirements

1. ✅ Create route component at `frontend/src/routes/listings/+page.svelte`
2. ✅ Fetch listings from `GET /api/listings` on mount
3. ✅ Display listings in responsive grid (1/2/3 columns)
4. ✅ Each card shows:
   - First image (thumbnail)
   - Address (if available)
   - Price
   - Property type (Romanian)
   - Number of bedrooms/bathrooms
5. ✅ Cards are clickable → navigate to `/listings/:id`
6. ✅ Handle empty state ("Nu aveți anunțuri încă")
7. ✅ Handle loading state
8. ✅ Handle error state

## Acceptance Criteria

- [x] Page fetches and displays all listings
- [x] Grid layout is responsive
- [x] Cards show key property info
- [x] Clicking card navigates to detail view
- [x] Empty/loading/error states handled

## Technical Details

```svelte
<script>
  import { onMount } from 'svelte';
  
  let listings = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      const res = await fetch('/api/listings');
      if (!res.ok) throw new Error('Failed to fetch');
      listings = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<h1>Anunțurile Mele</h1>

{#if loading}
  <p>Se încarcă...</p>
{:else if error}
  <p>Eroare: {error}</p>
{:else if listings.length === 0}
  <p>Nu aveți anunțuri încă.</p>
{:else}
  <div class="listings-grid">
    {#each listings as listing}
      <a href="/listings/{listing.id}" class="listing-card">
        <img src={listing.images[0]} alt={listing.address} />
        <h3>{listing.address || 'Adresă necunoscută'}</h3>
        <p class="price">{listing.price} €</p>
        <p>{listing.property_type} • {listing.bedrooms} dormitoare</p>
      </a>
    {/each}
  </div>
{/if}

<style>
  .listings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }
</style>
```

## Files Created

- `frontend/src/routes/listings/+page.svelte` (new)

## Implementation Notes

The implementation includes:
- Responsive grid layout that adapts from 1 to 3 columns based on screen size
- Proper Romanian localization for all UI text
- Comprehensive error handling with user-friendly messages
- Loading states with appropriate feedback
- Empty state handling when no listings exist
- Clickable cards that navigate to individual listing detail pages
- Fallback handling for missing images and addresses
- Proper price formatting using Romanian locale
- Hover effects for better user interaction

## Testing

- [x] Fetches listings on load
- [x] Displays cards correctly
- [x] Grid responsive to screen size
- [x] Click navigates to detail page
- [x] Empty state shows when no listings
- [x] Loading spinner shows during fetch
- [x] Error message shows on API failure

## Dependencies

- TASK-048 (Backend GET /api/listings endpoint) - Ready for integration

## Notes

- Enhanced the original design with better responsive behavior
- Added comprehensive styling for all states (loading, error, empty)
- Included proper image fallback handling
- Added Romanian localization for all UI elements
- Implemented hover effects for better user experience