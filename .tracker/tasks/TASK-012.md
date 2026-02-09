# TASK-012: Build image upload flow with backend integration

**Story:** STORY-005
**Status:** done
**Priority:** high
**Estimated:** 3h

## Description

Create the image upload UI component and wire it to the backend `/api/analyze-step` endpoint. This is the entry point for the user journey.

## Technical Requirements

- Drag-and-drop upload zone
- File type validation (jpg, png, webp)
- File size limit (e.g., 10MB)
- Preview uploaded image
- Loading state during backend processing
- Error handling for upload failures
- Send image to backend and process response

## Definition of Done

- [x] Upload component created with drag-and-drop
- [x] File validation implemented
- [x] Image preview displays after upload
- [x] Loading spinner shows during API call
- [x] Backend integration working
- [x] Response updates form state/schema
- [x] Error messages display for failures
