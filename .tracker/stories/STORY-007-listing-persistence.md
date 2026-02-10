# STORY-007: Listing Data Persistence & Save Functionality

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-10

## Description

Enable users to review all collected data (images, AI analysis, form fields) and save their complete property listing to the database. This is the final step that persists all the work done during the listing creation flow.

Currently, users can upload images, get AI analysis, fill in form fields, and see a preview (STORY-006 / TASK-030), but there's no way to actually **save** the listing to the database.

## User Story

> **As a** home seller  
> **I want to** review all my entered data and save my complete listing  
> **So that** my property information is stored and can be published or edited later

## User Journey

1. **Data Collection Phase:**
   - User uploads property images
   - AI analyzes images and extracts features
   - User fills in progressive form fields
   - Completion reaches 100%

2. **Review Phase (Already Implemented - TASK-030):**
   - User sees comprehensive preview page
   - All images displayed in gallery
   - Full property description shown
   - All form fields organized by category

3. **Save Phase (This Story):**
   - User clicks "Save Listing" or "Publish" button
   - Frontend sends complete listing data to backend
   - Backend validates and saves to database
   - User receives confirmation
   - Listing ID returned for future reference

## Key Requirements

### Backend
- **New endpoint:** `POST /api/listings/save` or `POST /api/listings`
- Accept complete listing payload:
  ```json
  {
    "property_data": {
      "property_type": "apartment",
      "price": 350000,
      "bedrooms": 2,
      "bathrooms": 1,
      // ... all form fields
    },
    "synthesis_data": {
      "total_rooms": 1,
      "layout_type": "open_concept",
      "unified_description": "...",
      "room_breakdown": {...},
      "amenities": [...]
    },
    "image_data": [
      {
        "url": "...",
        "analysis": {
          "description": "...",
          "rooms": {...},
          "amenities": [...]
        }
      }
    ]
  }
  ```
- **Validate** all required fields
- **Save to database:**
  - Main listing record
  - Associated images with analysis
  - Synthesis data
  - Timestamps (created_at, updated_at)
- **Return listing ID** and confirmation

### Frontend
- **Save button** on preview page (already present in TASK-030)
- **Loading state** during save
- **Success confirmation:**
  - Show success message
  - Display listing ID
  - Offer "View Listing" or "Create Another" options
- **Error handling:**
  - Show validation errors
  - Allow user to go back and fix
  - Don't lose entered data

### Database Schema
Need tables for:
- **listings** (main table)
  - id (primary key)
  - user_id (optional - future auth)
  - property_type
  - price
  - bedrooms, bathrooms, etc. (all form fields)
  - status (draft, published, archived)
  - created_at, updated_at

- **listing_images** (one-to-many)
  - id
  - listing_id (foreign key)
  - image_url or image_data (base64/blob)
  - ai_description
  - detected_rooms (JSON)
  - detected_amenities (JSON)
  - order_index

- **listing_synthesis** (one-to-one)
  - id
  - listing_id (foreign key)
  - total_rooms
  - layout_type
  - unified_description
  - room_breakdown (JSON)
  - property_overview (JSON)

## Acceptance Criteria

- [ ] User can review all entered data on preview page
- [ ] User can click "Save Listing" button
- [ ] Frontend sends complete listing payload to backend
- [ ] Backend validates required fields (property_type, price minimum)
- [ ] Backend saves listing to database (listings table)
- [ ] Backend saves associated images (listing_images table)
- [ ] Backend saves synthesis data (listing_synthesis table)
- [ ] Backend returns listing ID and success response
- [ ] Frontend shows success confirmation with listing ID
- [ ] User can create another listing after saving
- [ ] Error handling works (validation errors, database errors)
- [ ] Saved listing can be retrieved from database

## Technical Approach

### Phase 1: Database Schema (Task 1)
Create SQLAlchemy models for:
- `Listing` (main listing table)
- `ListingImage` (images with AI analysis)
- `ListingSynthesis` (property overview)

### Phase 2: Backend API (Task 2)
Implement `POST /api/listings` endpoint:
- Accept complete listing payload
- Validate data
- Save to database (transaction)
- Return listing ID

### Phase 3: Frontend Integration (Task 3)
Wire up the "Save Listing" button:
- Collect all data (form fields + synthesis + images)
- POST to `/api/listings`
- Handle success/error responses
- Show confirmation UI

### Phase 4: Testing (Task 4) - **MANDATORY BEFORE PUSH**
- Unit tests for database models
- Integration tests for save endpoint
- **E2E tests (Playwright):** Complete flow → save → verify in database
- **All tests MUST pass locally before git push**
- Run: `cd frontend && npm run test:e2e`
- Run: `cd backend && pytest`

## Tasks

- **TASK-031:** Create database schema and SQLAlchemy models for listings
- **TASK-032:** Implement `/api/listings` POST endpoint for saving
- **TASK-033:** Wire up frontend "Save Listing" button with backend
- **TASK-034:** Add listing retrieval endpoint (`GET /api/listings/:id`)
- **TASK-035:** Add success confirmation UI and "Create Another" flow
- **TASK-036:** Write E2E tests for complete save flow (**MUST RUN LOCALLY BEFORE PUSH**)

## Testing Requirements (MANDATORY)

**Before ANY git push to main:**
1. ✅ Backend unit tests pass: `cd backend && pytest`
2. ✅ Frontend builds: `cd frontend && npm run build`
3. ✅ E2E tests pass: `cd frontend && npm run test:e2e`
4. ✅ Manual verification with test images

**E2E Test Coverage Required:**
- Complete user journey: Upload images → Fill form → Preview → Save
- Verify listing saved to database
- Verify all fields persisted correctly
- Verify images and synthesis data saved
- Verify success confirmation displayed
- Test error cases (validation failures, database errors)

## Dependencies

- **STORY-006 (Listing Preview):** Provides the UI where save button exists
- **STORY-002 (Dynamic Form):** Provides the form data to save
- **STORY-004 (AI Analysis):** Provides synthesis data to save

## Success Metrics

- Users can successfully save listings
- Saved listings are retrievable from database
- No data loss during save process
- Average save time < 2 seconds
- User satisfaction with save confirmation

## Notes

### Image Storage Options
**Option A:** Store images as base64 in database (simple, but large)
**Option B:** Store images in file system, save paths in database
**Option C:** Use cloud storage (S3), save URLs in database

**Recommendation:** Start with Option A (base64 in DB) for MVP, migrate to Option C later for production.

### Data Validation
Required fields at minimum:
- `property_type`
- At least 1 image
- Basic contact info (if we add user auth)

Optional but recommended:
- Price (or "Contact for price")
- Location (city, state)

### Future Enhancements
- User authentication (listings belong to users)
- Draft vs Published status
- Edit saved listings
- Delete/archive listings
- Search and filter saved listings
- Export listing data

## Open Questions

1. **User Authentication:** Do we need user accounts now or later?
   - *Decision:* Later. For MVP, listings are anonymous (anyone can save)

2. **Image Storage:** Base64 in DB or external storage?
   - *Decision:* Base64 in DB for MVP, migrate to S3/cloud storage later

3. **Listing Status:** Do we need draft/published states now?
   - *Decision:* Yes. Start with "draft" and "published" statuses

4. **Edit Functionality:** Can users edit after saving?
   - *Decision:* Phase 2. For now, just create and save (no edit)

## Related Stories

- **STORY-006:** Multi-Image Analysis (provides data to save)
- **STORY-002:** Dynamic Form Infrastructure (provides form data)
- **STORY-004:** AI Analysis Logic (provides synthesis data)
- **Future:** User authentication and listing management
- **Future:** Public listing pages and search
