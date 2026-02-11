# STORY-001: Sidebar Navigation and Listing Management

**Created:** 2026-02-11  
**Status:** In Progress  
**Priority:** High

## User Story

As a user, I want to navigate between creating new ads and viewing my existing listings via a sidebar menu, so I can easily manage all my property listings from one interface.

## Acceptance Criteria

1. ✅ Left sidebar menu is visible on all pages
2. ✅ Menu has two main options:
   - "Create New Ad" (links to existing form)
   - "My Listings" (shows all saved listings)
3. ✅ Listings page shows all saved ads in a simple list
4. ✅ User can click a listing to view its full details
5. ✅ Listing detail view shows all property data (images, description, amenities, etc.)

## Technical Requirements

### Frontend
- Left sidebar component (fixed position)
- Listings list view page (`/listings`)
- Listing detail view page (`/listings/:id`)
- Routing configuration
- Integration with existing layout

### Backend
- GET `/api/listings` - Return all listings
- GET `/api/listings/:id` - Return single listing with full data
- Pagination support (optional for v1)

## Tasks

- [ ] TASK-044: Create left sidebar navigation component
- [ ] TASK-045: Create listings list view page
- [ ] TASK-046: Create listing detail view page
- [ ] TASK-047: Add routing for listing views
- [ ] TASK-048: Backend - Add GET /api/listings endpoint
- [ ] TASK-049: Backend - Add GET /api/listings/:id endpoint
- [ ] TASK-050: Integrate sidebar into main app layout

## Design Notes

**Sidebar:**
- Fixed left position, ~200-250px wide
- Romanian labels: "Creează Anunț Nou", "Anunțurile Mele"
- Active state highlighting
- Mobile: Collapsible hamburger menu

**Listings List:**
- Simple card layout
- Show: thumbnail, address, price, property type
- Responsive grid (1-2-3 columns based on screen size)

**Listing Detail:**
- Full-width layout
- Image gallery at top
- Property details in organized sections
- Match preview layout style

## Implementation Order

1. Backend endpoints (TASK-048, TASK-049)
2. Sidebar component (TASK-044)
3. List view (TASK-045)
4. Detail view (TASK-046)
5. Routing (TASK-047)
6. Integration (TASK-050)

## Dependencies

- Existing listing save functionality ✅
- Database schema supports listing retrieval ✅
- Frontend routing library (svelte-routing or similar)

## Out of Scope (Future Stories)

- Edit existing listings
- Delete listings
- Search/filter listings
- User authentication (multi-user support)
- Pagination UI
