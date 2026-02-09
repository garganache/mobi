# STORY-005: AI-Guided User Journey Integration

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-09

## Description

Bring together the dynamic form infrastructure (STORY-002) and the AI orchestrator (STORY-003, STORY-004) to create the complete user experience. This is where users see the "magic" of an interface that evolves as they provide information.

The journey starts with a simple image upload and progressively reveals relevant fields based on AI analysis, creating a conversational, guided experience rather than a static form.

## Key Requirements

- Initial "hook" screen with prominent image upload
- Backend integration: send data to `/api/analyze-step` and process responses
- Progressive field reveal with smooth animations
- AI message display showing guidance at each step
- Visual split: uploaded content on one side, form fields on the other
- Real-time updates: as user fills fields, AI may suggest new ones

## User Journey Flow

1. **Landing**: User sees "Drop a photo to start your listing"
2. **Upload**: User drops kitchen photo → loading state
3. **AI Response**: "I see a modern kitchen! Is this a house or an apartment?"
4. **Selection**: User clicks "Apartment" → house-only fields hidden
5. **Progressive**: 2-3 relevant fields appear with guidance
6. **Iteration**: As user fills fields, more relevant fields may appear

## Acceptance Criteria

- [ ] Image upload UI implemented with drag-and-drop
- [ ] Upload triggers backend call with loading state
- [ ] Backend response updates form schema dynamically
- [ ] New fields appear with smooth animations
- [ ] AI guidance messages display prominently
- [ ] User can see their uploaded images alongside the form
- [ ] Form state persists across interactions
- [ ] Complete flow works end-to-end for at least one scenario

## Tasks

- TASK-012: Build image upload flow with backend integration
- TASK-013: Implement progressive field reveal with animations
- TASK-014: Add AI messaging and guidance prompts display
- TASK-015: Create end-to-end flow testing for complete user journey
- TASK-025: Write Playwright E2E tests for complete user journey
- TASK-026: Write Playwright tests for image upload flow
- TASK-027: Write Playwright tests for progressive field reveal
- TASK-028: Write Playwright tests for AI guidance interactions

## Notes

Focus on making the experience feel like a co-pilot session, not an interrogation. The AI should feel helpful, not intrusive.

Consider adding a "preview" of the listing as it's being built to show users the value of providing more information.
