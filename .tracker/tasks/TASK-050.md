# TASK-050: Integrate Sidebar into Main App Layout

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Complete  
**Priority:** Medium  
**Estimated:** 15 min

## Objective

Integrate the Sidebar component into the main app layout so it appears on all pages.

## Requirements

1. Import and render Sidebar component in main layout
2. Adjust main content area to account for sidebar width
3. Ensure sidebar is visible on all routes
4. Ensure page scrolling works correctly
5. Mobile: Sidebar should collapse/overlay on small screens

## Acceptance Criteria

- [ ] Sidebar visible on all pages
- [ ] Main content doesn't overlap with sidebar
- [ ] Layout responsive on mobile
- [ ] No z-index or positioning issues
- [ ] Scrolling works as expected

## Technical Details

```svelte
<!-- frontend/src/routes/+layout.svelte (SvelteKit) -->
<!-- OR frontend/src/App.svelte (svelte-routing) -->

<script>
  import Sidebar from '$lib/components/Sidebar.svelte';
</script>

<div class="app-container">
  <Sidebar />
  <main class="main-content">
    <slot />  <!-- SvelteKit -->
    <!-- OR <Router>...</Router> for svelte-routing -->
  </main>
</div>

<style>
  .app-container {
    display: flex;
    min-height: 100vh;
  }
  
  .main-content {
    flex: 1;
    margin-left: 250px; /* Sidebar width */
    padding: 2rem;
  }
  
  @media (max-width: 768px) {
    .main-content {
      margin-left: 0; /* Full width on mobile */
    }
  }
</style>
```

## Files to Create/Modify

- `frontend/src/routes/+layout.svelte` (SvelteKit)
- OR `frontend/src/App.svelte` (svelte-routing)

## Testing

- [ ] Sidebar appears on home page
- [ ] Sidebar appears on listings page
- [ ] Sidebar appears on detail page
- [ ] Main content positioned correctly
- [ ] Mobile layout collapses properly
- [ ] No visual glitches or overlaps
- [ ] Navigation from sidebar works

## Dependencies

- TASK-044 (Sidebar component)
- TASK-047 (Routing configured)

## Notes

- Use CSS Grid or Flexbox for layout
- Ensure sidebar has higher z-index than main content if needed
- Test on various screen sizes
- Consider sticky positioning if needed for long pages
- Mobile hamburger menu should overlay content, not push it
