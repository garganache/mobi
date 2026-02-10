# TASK-029: Multi-Image Analysis with Correlation & Synthesis

**Story:** STORY-006
**Status:** done
**Priority:** high
**Estimated:** 6h

## Description

Implement multi-image batch analysis that correlates results from multiple property images and generates a unified, coherent summary of the entire property.

Currently, `analyze_property_image()` processes images independently. When a user uploads 6 room images, we get 6 separate descriptions with no understanding of the overall property.

**New capability needed:**
- Accept multiple images (e.g., 6 room photos)
- Analyze each individually
- **Correlate** the results: count total rooms, identify unique spaces, combine amenities
- **Synthesize** a unified summary: "6 rooms total: 2 bedrooms with hardwood floors, 1 kitchen with granite counters and stainless appliances, 1 living room with fireplace, 1 bathroom with tile, 1 hallway"

## User Story

> "I upload 6 images of different rooms. The system should analyze each, then tell me: how many rooms total, what's in each room (floors, windows, fixtures), and give me one coherent description of the entire property - not 6 disconnected descriptions."

## Technical Approach

### 1. Create `analyze_multiple_images()` function

```python
def analyze_multiple_images(
    images: List[bytes],
    model_type: str = "mock",
    **model_kwargs
) -> Dict[str, Any]:
    """
    Analyze multiple property images and synthesize unified results.
    
    Args:
        images: List of image data (bytes)
        model_type: Vision model to use
        **model_kwargs: Model configuration
        
    Returns:
        {
            "individual_analyses": [...],  # Each image's analysis
            "synthesis": {
                "total_rooms": 6,
                "room_breakdown": {
                    "bedroom": 2,
                    "kitchen": 1,
                    "living_room": 1,
                    "bathroom": 1,
                    "hallway": 1
                },
                "amenities_by_room": {
                    "bedroom_1": ["hardwood_floors", "large_window"],
                    "bedroom_2": ["hardwood_floors", "closet"],
                    "kitchen": ["granite_counters", "stainless_steel", "dishwasher"],
                    ...
                },
                "unified_description": "This property has 6 rooms...",
                "property_overview": {...}
            }
        }
    """
```

### 2. Synthesis Logic

```python
def synthesize_property_overview(analyses: List[Dict]) -> Dict:
    """
    Correlate multiple image analyses into unified property description.
    
    - Count total rooms across all images
    - Identify unique room types
    - Aggregate amenities per room
    - Detect patterns (e.g., "hardwood throughout")
    - Generate coherent narrative
    """
```

### 3. Room Correlation

**Challenge:** Multiple images might show the same room from different angles.

**Solution (Phase 1 - Simple):**
- Assume each image = different room
- User can later indicate if images overlap

**Solution (Phase 2 - Smart):**
- Use vision model to detect if 2 images are the same room
- "Does image 1 and image 2 show the same space?"

## API Changes

### New Endpoint: `/api/analyze-batch`

```python
@app.post("/api/analyze-batch")
async def analyze_batch_images(files: List[UploadFile]):
    """Analyze multiple images and return correlated results."""
    image_data = [await file.read() for file in files]
    
    result = analyze_multiple_images(
        images=image_data,
        model_type=os.getenv("VISION_MODEL", "mock")
    )
    
    return {
        "status": "success",
        "individual_analyses": result["individual_analyses"],
        "synthesis": result["synthesis"]
    }
```

### Existing Endpoint Enhancement

Keep `/api/listings` for single-image upload, add optional batch mode:

```python
files: List[UploadFile] = Form(None)  # Multiple files
```

## Frontend Changes

### Upload Multiple Images

```typescript
// Allow multiple file selection
<input type="file" multiple accept="image/*" onChange={handleMultipleUpload} />

// Send batch request
const formData = new FormData();
files.forEach(file => formData.append('images', file));

const response = await fetch('/api/analyze-batch', {
  method: 'POST',
  body: formData
});

const { synthesis } = await response.json();
// Display unified summary
```

### Display Synthesis

Show both:
1. **Individual analyses** (collapsible cards per image)
2. **Unified summary** (prominent, top-level)

```
┌─────────────────────────────────────────┐
│ Property Overview (6 rooms analyzed)    │
│                                         │
│ 🏠 6 rooms total:                       │
│   • 2 Bedrooms (hardwood floors)        │
│   • 1 Kitchen (granite, stainless)      │
│   • 1 Living room (fireplace)           │
│   • 1 Bathroom (tile)                   │
│   • 1 Hallway                           │
│                                         │
│ Overall: Modern apartment style         │
└─────────────────────────────────────────┘

▼ View Individual Room Analyses
  ├─ Image 1: Kitchen
  ├─ Image 2: Bedroom 1
  └─ ...
```

## Definition of Done

- [x] `analyze_multiple_images()` function implemented in `vision_model.py`
- [x] `synthesize_property_overview()` correlation logic implemented
- [x] Mock model returns realistic multi-image synthesis
- [x] `/api/analyze-batch` endpoint created and tested
- [x] Unit tests for synthesis logic
- [x] Frontend supports multiple image upload
- [x] Frontend displays unified summary + individual results
- [x] Integration test: upload 6 images → verify unified output
- [x] Documentation updated with multi-image API usage

## Test Cases

### Unit Tests
- `test_analyze_multiple_images_mock()`: 3 images → correct room count
- `test_synthesis_aggregates_amenities()`: Verify amenities grouped by room
- `test_synthesis_generates_description()`: Verify narrative is coherent

### Integration Tests
- Upload 6 different room images → verify synthesis
- Upload 2 images of same room (different angles) → verify deduplication (Phase 2)

## Notes

- Start with **Phase 1**: Assume each image = unique room
- **Phase 2** (future): Smart room deduplication via vision model
- Consider adding "Mark as duplicate" UI control for manual override

## Blocked By

None - can start immediately

## Dependencies

- Existing `analyze_property_image()` function
- Existing vision model infrastructure
