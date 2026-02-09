# STORY-004: AI Analysis & Field Suggestion Logic

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-09

## Description

Implement the AI intelligence layer that analyzes user input (primarily images) to extract property features and determine which fields are most relevant to show next. This is the "brain" that makes the interface adaptive.

The system should identify property characteristics (house vs apartment, features like pool/garage/kitchen type) and intelligently suggest only the relevant fields, avoiding overwhelming users with irrelevant options.

## Key Requirements

- Image analysis capability (vision model integration or mock)
- Feature extraction logic: property type, rooms, amenities, style
- Field relevance algorithm: determine which fields matter based on detected features
- Confidence scoring: track how certain the AI is about detections
- Progressive disclosure rules: prioritize 2-3 most important missing fields

## Acceptance Criteria

- [ ] Image analysis returns structured feature data
- [ ] Property type detection works (house/apartment/land)
- [ ] Feature detection identifies at least 5 common amenities (pool, garage, etc.)
- [ ] Field suggestion algorithm returns prioritized list of next fields
- [ ] Irrelevant fields are filtered out (e.g., no barn fields for apartments)
- [ ] System handles images with low confidence gracefully

## Tasks

- TASK-009: Integrate vision model for image analysis (mock initially, then real)
- TASK-010: Build feature extraction logic (property type, amenities, style)
- TASK-011: Implement field suggestion algorithm based on missing data
- TASK-022: Write unit tests for feature extraction logic
- TASK-023: Write unit tests for field suggestion algorithm
- TASK-024: Write tests for vision model integration (mocked)

## Notes

Start with mock/rule-based vision analysis. Can use placeholder responses like "if image contains 'pool' → suggest pool_type field". Real vision model integration can come later.

Consider using multimodal LLM (GPT-4V, Claude Vision) for both image analysis and field suggestion in one call.
