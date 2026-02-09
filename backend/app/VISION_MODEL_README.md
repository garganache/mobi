# Vision Model Integration

This module provides image analysis capabilities for property listings using vision models.

## Overview

The vision model integration supports both mock and real vision models:

- **Mock Vision Model**: Returns predefined responses for testing and development
- **OpenAI GPT-4V**: Real vision model using OpenAI's GPT-4 Vision API
- **Anthropic Claude**: Real vision model using Anthropic's Claude vision capabilities

## Usage

### Basic Usage

```python
from app.vision_model import analyze_property_image

# Analyze with mock model (default)
result = analyze_property_image(image_bytes)

# Analyze with real model
result = analyze_property_image(image_bytes, model_type="openai")
```

### Configuration

Set environment variables for real models:

```bash
# For OpenAI
OPENAI_API_KEY=your_api_key_here

# For Anthropic
ANTHROPIC_API_KEY=your_api_key_here
```

### Response Format

The vision model returns structured data:

```json
{
  "description": "A modern kitchen with granite countertops and stainless steel appliances",
  "property_type": "apartment",
  "rooms": {"kitchen": 1, "bedroom": 2},
  "amenities": ["granite_counters", "stainless_steel", "dishwasher"],
  "style": "modern",
  "materials": ["granite_counters", "stainless_steel"],
  "confidence_scores": {
    "property_type": 0.9,
    "style": 0.85,
    "amenities": 0.8
  }
}
```

## Integration with Main Application

The vision model is integrated into the `/analyze-step` endpoint. When an image is uploaded:

1. Image is preprocessed (resized, format conversion)
2. Vision model analyzes the image
3. Results are extracted and mapped to form fields
4. AI message is generated based on detected features

## Error Handling

- Invalid images fall back to default values
- API failures are logged and handled gracefully
- Mock model is used when real models are unavailable

## Testing

Run the vision model tests:

```bash
cd /home/ubuntu/mobi/backend
source .venv/bin/activate
python -m pytest tests/test_feature_extraction.py -v
```

## Future Enhancements

- Add more vision model providers (Google Vision, Azure Computer Vision)
- Implement caching for repeated image analysis
- Add confidence-based filtering
- Support for video analysis
- Custom model training for property-specific features