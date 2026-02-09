# STORY-003: FastAPI Orchestrator Endpoint

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-09

## Description

Create a Python FastAPI endpoint that acts as an "Intelligent Orchestrator" for the listing creation process. This endpoint receives the current form state and optional new input (like an image), then returns a UI manifest telling the Svelte frontend which fields to display next.

The endpoint should return both extracted data (what the AI found) and instructions (what UI components to render).

## Key Requirements

- `/api/analyze-step` endpoint accepting JSON with `current_data` and optional `new_input`
- Return structured "UI Manifest" with:
  - `extracted_data`: Key-value pairs of detected features
  - `ui_schema`: Array of field definitions (component_type, id, label, options)
  - `ai_message`: Friendly guidance text for the user
- Stateless design (all context passed in request)
- Handle different input types (image upload, text fields)

## Acceptance Criteria

- [ ] `/api/analyze-step` endpoint created and responds with correct schema
- [ ] UI Manifest schema designed and documented
- [ ] Endpoint accepts multipart/form-data for image uploads
- [ ] Returns appropriate field suggestions based on input type
- [ ] AI message is contextual and helpful
- [ ] Endpoint tested with sample requests

## Tasks

- TASK-006: Create /api/analyze-step endpoint accepting current_data and new_input
- TASK-007: Design and document UI manifest JSON schema
- TASK-008: Implement basic orchestration logic for field prioritization
- TASK-019: Write unit tests for /api/analyze-step endpoint
- TASK-020: Write integration tests for UI manifest generation
- TASK-021: Write tests for different input types handling

## Notes

Initial implementation can use simple rule-based logic before integrating actual vision AI models.
