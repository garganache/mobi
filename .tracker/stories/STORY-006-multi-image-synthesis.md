# STORY-006: Multi-Image Analysis & Property Synthesis

**Status:** todo
**Priority:** high
**Epic:** EPIC-001
**Created:** 2026-02-10

## Description

Enable users to upload multiple property images (e.g., 6 room photos) and receive a unified, coherent analysis of the entire property rather than disconnected individual image descriptions.

Currently, the system analyzes images independently with no understanding of how they relate to each other. When a user uploads photos of their kitchen, bedroom, living room, and bathroom, they get 4 separate analyses. This story adds the intelligence to correlate those analyses and synthesize a holistic property overview.

**The Goal:** Transform multiple isolated room descriptions into a complete property narrative that answers questions like:
- How many total rooms are in this property?
- What features are in each specific room?
- What's the overall style and condition?
- Are there patterns across rooms (e.g., "hardwood floors throughout")?

## User Story

> **As a** home seller preparing my listing  
> **I want to** upload multiple photos of different rooms in my property  
> **So that** the system understands my entire property and can generate one coherent description instead of treating each room as an isolated entity

### Example Scenario

**Before (current behavior):**
```
User uploads 6 images
→ Image 1: "A modern kitchen with granite countertops"
→ Image 2: "A bedroom with hardwood floors"
→ Image 3: "A bathroom with tile"
→ Image 4: "A living room with fireplace"
→ Image 5: "A bedroom with carpet"
→ Image 6: "A hallway"

Result: 6 disconnected descriptions
```

**After (with synthesis):**
```
User uploads 6 images
→ System analyzes each image individually
→ System correlates and synthesizes results

Result: "This property has 6 rooms:
  • 2 Bedrooms (1 with hardwood, 1 with carpet)
  • 1 Modern kitchen with granite counters and stainless appliances
  • 1 Living room with fireplace
  • 1 Bathroom with tile
  • 1 Hallway
  
Overall style: Modern with mixed flooring materials.
Notable features: Granite kitchen, fireplace in living room."
```

## Key Requirements

### Backend
- **Batch Analysis API**: Accept multiple images in a single request
- **Correlation Logic**: Identify room types, count total rooms, detect duplicates
- **Synthesis Engine**: Aggregate features, amenities, and materials across all images
- **Smart Aggregation**: Detect patterns (e.g., "hardwood throughout" if 4/6 rooms have it)
- **Narrative Generation**: Create coherent unified description from individual analyses

### Frontend
- **Multi-File Upload**: Allow users to select and upload multiple images simultaneously
- **Unified Summary Display**: Show synthesized property overview prominently
- **Individual Image Cards**: Collapsible section showing per-image analysis
- **Room Correlation UI**: (Future) Allow users to mark "these 2 photos are the same room"

### Data Model
- Store both individual image analyses AND synthesized overview
- Support relationship between images and the unified property description

## Acceptance Criteria

- [ ] User can upload 2-10 images in a single batch
- [ ] System analyzes each image individually using existing vision model
- [ ] System counts total unique rooms across all images
- [ ] System aggregates amenities per room type
- [ ] System detects common patterns (e.g., flooring type across multiple rooms)
- [ ] System generates a unified property description that reads naturally
- [ ] Frontend displays both:
  - Prominent unified summary (e.g., "6 rooms, 2 bedrooms...")
  - Expandable individual image analyses
- [ ] API response includes both `individual_analyses` and `synthesis` objects
- [ ] Mock model returns realistic multi-room scenarios for testing
- [ ] Integration test: upload 6 different room images → verify correct synthesis

## Technical Approach

### Phase 1: Basic Aggregation (MVP)
- Assume each image = unique room (no duplicate detection)
- Count rooms by type
- Aggregate amenities per room
- Generate simple unified description

### Phase 2: Smart Correlation (Future)
- Detect if multiple images show same room from different angles
- Use vision model to compare images: "Are these the same space?"
- Allow user to manually mark duplicates
- More sophisticated narrative generation

## Tasks

- TASK-029: Implement multi-image analysis with correlation & synthesis
  - Create `analyze_multiple_images()` function
  - Implement `synthesize_property_overview()` correlation logic
  - Add `/api/analyze-batch` endpoint
  - Update frontend for batch upload
  - Create tests for synthesis logic

## Dependencies

- **STORY-004 (AI Analysis & Field Suggestion Logic)**: Provides the foundation `analyze_property_image()` function that multi-image analysis builds upon
- **STORY-003 (FastAPI Orchestrator)**: Backend API infrastructure for new batch endpoint

## Success Metrics

- User uploads average of 4+ images per listing (vs 1-2 currently)
- Synthesized descriptions are rated as "coherent and accurate" by users
- Time to create complete listing decreases (fewer manual field fills needed)
- User satisfaction: "The system understands my whole property"

## UX Considerations

### Primary Use Case
Users creating a listing typically have 5-20 photos of their property. They want the system to "see" the whole place, not just individual snapshots.

### Visual Design
```
┌─────────────────────────────────────────────────────────┐
│  📸 Upload Multiple Photos                              │
│  [Drag & drop 6 images here or click to select]        │
└─────────────────────────────────────────────────────────┘

After Upload:

┌─────────────────────────────────────────────────────────┐
│  🏠 Property Overview (Analyzed 6 rooms)                │
│                                                         │
│  Your property has 6 rooms:                             │
│  ✓ 2 Bedrooms                                           │
│     - Bedroom 1: Hardwood floors, large closet          │
│     - Bedroom 2: Carpet, built-in shelving              │
│  ✓ 1 Kitchen: Granite counters, stainless appliances    │
│  ✓ 1 Living Room: Fireplace, hardwood floors            │
│  ✓ 1 Bathroom: Tile floors, updated fixtures            │
│  ✓ 1 Hallway                                            │
│                                                         │
│  Overall Style: Modern with traditional elements        │
│  Condition: Well-maintained                             │
│                                                         │
│  ▼ View Individual Room Analysis                       │
└─────────────────────────────────────────────────────────┘
```

### Guidance Messages
- Before upload: "Upload photos of each room to get a complete property analysis"
- During processing: "Analyzing 6 images... 4/6 complete"
- After synthesis: "I analyzed 6 rooms. Here's what I found:"

## Notes

- Start with Phase 1 (no duplicate detection) to prove the value
- Consider adding confidence scores to synthesis (e.g., "High confidence: 6 unique rooms")
- Future enhancement: Suggest which photos are missing ("I don't see a bathroom photo yet")
- Could extend to floor plan generation: use multi-image analysis to infer layout

## Related Stories

- **STORY-004**: Provides single-image analysis capability (dependency)
- **STORY-005**: User journey integration (this enhances the upload flow)
- **Future STORY**: Floor plan generation from multiple images
- **Future STORY**: Missing photo suggestions ("Upload bathroom photo for complete listing")

## Open Questions

1. **Duplicate Detection**: How important is it to detect same room from different angles in MVP?
   - *Decision:* Not critical for Phase 1. Add manual "mark as duplicate" control instead.

2. **Max Images**: What's reasonable upper limit?
   - *Decision:* Cap at 10 images for MVP to control costs and processing time.

3. **Processing Time**: If analyzing 10 images, could take 30+ seconds. Acceptable?
   - *Decision:* Use progress indicator. Consider async processing if too slow.

4. **Cost**: Vision API calls for 10 images = 10x cost vs single image.
   - *Decision:* Acceptable for MVP. Optimize with caching and smarter prompting later.
