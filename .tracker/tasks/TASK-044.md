# TASK-044: Create Left Sidebar Navigation Component

**Story:** STORY-001  
**Created:** 2026-02-11  
**Status:** Complete  
**Priority:** High  
**Estimated:** 30 min

## Objective

Create a reusable left sidebar component with navigation menu for the Mobi app.

## Requirements

1. Create `Sidebar.svelte` component in `frontend/src/lib/components/`
2. Fixed left position, 250px wide on desktop
3. Two menu items:
   - "Creează Anunț Nou" → `/` (home/create page)
   - "Anunțurile Mele" → `/listings` (listings page)
4. Active state highlighting for current route
5. Responsive: collapsible on mobile (<768px)
6. Match existing app styling (colors, fonts)

## Acceptance Criteria

- [x] Component renders correctly
- [x] Navigation links work
- [x] Active state shows current page
- [x] Mobile-responsive (hamburger menu)
- [x] Styled consistently with app

## Technical Details

```svelte
<!-- Sidebar.svelte -->
<script>
  import { page } from '$app/stores'; // or equivalent routing
  let isOpen = false; // for mobile
</script>

<aside class="sidebar" class:mobile-open={isOpen}>
  <nav>
    <a href="/" class:active={$page.url.pathname === '/'}>
      Creează Anunț Nou
    </a>
    <a href="/listings" class:active={$page.url.pathname.startsWith('/listings')}>
      Anunțurile Mele
    </a>
  </nav>
</aside>

<style>
  .sidebar { position: fixed; left: 0; width: 250px; ... }
  @media (max-width: 768px) { ... }
</style>
```

## Files to Create/Modify

- `frontend/src/lib/components/Sidebar.svelte` (new)

## Testing

- [ ] Sidebar visible on page load
- [ ] Links navigate correctly
- [ ] Active state updates on route change
- [ ] Mobile menu toggles properly

## Dependencies

- None (standalone component)

## Notes

- Use Romanian labels throughout
- Keep styling simple and clean
- Ensure z-index doesn't conflict with modals/overlays
