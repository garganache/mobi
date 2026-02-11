# TASK-047: Add Routing for Listing Views

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Todo  
**Priority:** Medium  
**Estimated:** 15 min

## Objective

Configure frontend routing to support the listings list and detail views.

## Requirements

1. Ensure routing library is installed (svelte-routing or SvelteKit routing)
2. Configure routes:
   - `/` → Existing create ad page
   - `/listings` → Listings list page (TASK-045)
   - `/listings/:id` → Listing detail page (TASK-046)
3. Ensure route parameters are accessible in components
4. Configure client-side navigation (no full page reloads)

## Acceptance Criteria

- [ ] All routes defined and accessible
- [ ] Navigation between routes works smoothly
- [ ] Route parameters passed correctly to components
- [ ] Browser back/forward buttons work
- [ ] URLs are shareable/bookmarkable

## Technical Details

If using SvelteKit (recommended):
```
frontend/src/routes/
  +page.svelte              # Home / Create ad
  listings/
    +page.svelte            # List all listings
    [id]/
      +page.svelte          # Single listing detail
```

Routes are automatic in SvelteKit based on folder structure.

If using svelte-routing:
```svelte
<!-- App.svelte -->
<script>
  import { Router, Route } from "svelte-routing";
  import Home from "./routes/Home.svelte";
  import ListingsPage from "./routes/listings/ListingsPage.svelte";
  import ListingDetail from "./routes/listings/ListingDetail.svelte";
</script>

<Router>
  <Route path="/" component={Home} />
  <Route path="/listings" component={ListingsPage} />
  <Route path="/listings/:id" component={ListingDetail} />
</Router>
```

## Files to Create/Modify

- SvelteKit: Folder structure in `frontend/src/routes/`
- OR: `frontend/src/App.svelte` (for svelte-routing)
- `package.json` (if installing routing library)

## Testing

- [ ] Navigate to `/` shows create ad page
- [ ] Navigate to `/listings` shows list page
- [ ] Navigate to `/listings/1` shows detail page
- [ ] Clicking links doesn't trigger full reload
- [ ] Back button works correctly
- [ ] Direct URL access works (refresh on /listings/1)

## Dependencies

- TASK-045 (List view component)
- TASK-046 (Detail view component)

## Notes

- Check if SvelteKit is already configured (preferred)
- If not SvelteKit, install `svelte-routing`: `npm install svelte-routing`
- Ensure vite.config.js has proper history fallback for SPA routing
- Test all routes after implementation
