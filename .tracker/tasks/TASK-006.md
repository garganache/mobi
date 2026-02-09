# TASK-006: Create /api/analyze-step endpoint accepting current_data and new_input

**Story:** STORY-003
**Status:** done
**Priority:** high
**Estimated:** 2h

## Description

Create the core FastAPI endpoint that will act as the orchestrator for the listing creation process. This endpoint receives the current form state and optional new input (image or text) and returns instructions for what the UI should display next.

## Technical Requirements

- Endpoint: `POST /api/analyze-step`
- Accept JSON body with:
  - `current_data`: dict of existing form values
  - `new_input`: optional base64 image or text snippet
  - `input_type`: 'image' | 'text' | 'field_update'
- Return UI Manifest (see TASK-007 for schema)
- Handle multipart/form-data for image uploads

## Definition of Done

- [x] Endpoint created in FastAPI app
- [x] Accepts required parameters
- [x] Returns valid JSON response
- [x] Handles missing/optional parameters gracefully
- [x] CORS configured if needed for local development
- [x] Endpoint documented with docstring
