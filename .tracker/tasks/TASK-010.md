# TASK-010: Build feature extraction logic (property type, amenities, style)

**Story:** STORY-004
**Status:** todo
**Priority:** high
**Estimated:** 3h

## Description

Build the logic that processes vision model output and extracts structured property features. Convert natural language descriptions into structured data that can drive field suggestions.

## Features to Extract

- **Property Type**: house, apartment, condo, townhouse, land
- **Amenities**: pool, garage, balcony, fireplace, deck, etc.
- **Style**: modern, traditional, contemporary, rustic
- **Rooms**: kitchen, bathroom, bedroom, living room
- **Materials**: hardwood floors, granite counters, stainless appliances

## Definition of Done

- [ ] Feature extraction function created
- [ ] Extracts at least 5 feature categories
- [ ] Returns structured data (dict/object)
- [ ] Handles ambiguous or missing information gracefully
- [ ] Confidence scores included (optional)
- [ ] Tested with various vision model outputs
