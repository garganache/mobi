# TASK-046: Create Listing Detail View Page

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Todo  
**Priority:** High  
**Estimated:** 45 min

## Objective

Create a page that displays full details of a single property listing.

## Requirements

1. Create route component at `frontend/src/routes/listings/[id]/+page.svelte`
2. Fetch single listing from `GET /api/listings/:id`
3. Display all listing data:
   - Image gallery (all images)
   - Property type, bedrooms, bathrooms, square feet
   - Price
   - Address
   - Description
   - Amenities by room
   - Any additional metadata
4. Layout similar to existing preview component
5. Handle loading/error/not found states
6. Back button to return to listings

## Acceptance Criteria

- [ ] Page fetches single listing by ID
- [ ] All listing data displayed
- [ ] Image gallery functional
- [ ] Layout clean and organized
- [ ] Loading/error/404 states handled
- [ ] Back navigation works

## Technical Details

```svelte
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  let listing = null;
  let loading = true;
  let error = null;
  
  onMount(async () => {
    const id = $page.params.id;
    try {
      const res = await fetch(`/api/listings/${id}`);
      if (res.status === 404) {
        error = 'Anunțul nu a fost găsit';
        return;
      }
      if (!res.ok) throw new Error('Failed to fetch');
      listing = await res.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p>Se încarcă...</p>
{:else if error}
  <div class="error">
    <p>{error}</p>
    <a href="/listings">← Înapoi la anunțuri</a>
  </div>
{:else if listing}
  <a href="/listings" class="back-link">← Înapoi la anunțuri</a>
  
  <div class="listing-detail">
    <div class="image-gallery">
      {#each listing.images as image}
        <img src={image} alt="Property" />
      {/each}
    </div>
    
    <div class="property-info">
      <h1>{listing.address || 'Adresă necunoscută'}</h1>
      <p class="price">{listing.price} €</p>
      <p>{listing.property_type} • {listing.bedrooms} dormitoare • {listing.bathrooms} băi</p>
      
      <section class="description">
        <h2>Descriere</h2>
        <p>{listing.description}</p>
      </section>
      
      {#if listing.amenities_by_room}
        <section class="amenities">
          <h2>Facilități</h2>
          {#each Object.entries(listing.amenities_by_room) as [room, amenities]}
            <div>
              <h3>{room}</h3>
              <ul>
                {#each amenities as amenity}
                  <li>{amenity}</li>
                {/each}
              </ul>
            </div>
          {/each}
        </section>
      {/if}
    </div>
  </div>
{/if}
```

## Files to Create/Modify

- `frontend/src/routes/listings/[id]/+page.svelte` (new)

## Testing

- [ ] Fetches correct listing by ID
- [ ] All data displays properly
- [ ] Images render in gallery
- [ ] 404 handled for invalid IDs
- [ ] Back link navigates to list
- [ ] Loading state shows during fetch
- [ ] Error handling works

## Dependencies

- TASK-049 (Backend GET /api/listings/:id endpoint) must be complete

## Notes

- Reuse styles from existing PreviewListing component where possible
- Ensure Romanian translations for all labels
- Image gallery can be simple for v1 (grid of images)
- Consider lazy loading images if many images present
