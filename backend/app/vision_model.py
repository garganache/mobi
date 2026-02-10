"""
Vision model integration for property image analysis.

This module provides both mock and real vision model implementations for analyzing
property images and extracting structured real estate data.
"""

import base64
import io
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from PIL import Image

logger = logging.getLogger(__name__)


class VisionModelError(Exception):
    """Base exception for vision model errors."""
    pass


class VisionModelInterface(ABC):
    """Abstract interface for vision models."""
    
    @abstractmethod
    def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """
        Analyze an image and return structured property data.
        
        Args:
            image_data: Raw image bytes
            prompt: Prompt to send to the vision model
            
        Returns:
            Dictionary containing analyzed property data
        """
        pass


class MockVisionModel(VisionModelInterface):
    """Mock vision model that returns predefined results for testing."""
    
    def __init__(self):
        self.mock_responses = {
            "kitchen": {
                "description": "A modern kitchen with granite countertops, stainless steel appliances, and hardwood floors. Features include a dishwasher, refrigerator, and stove.",
                "property_type": "apartment",
                "rooms": {"kitchen": 1, "bedroom": 2},
                "amenities": ["granite_counters", "stainless_steel", "dishwasher", "refrigerator", "stove", "hardwood_floors"],
                "style": "modern",
                "materials": ["granite_counters", "stainless_steel", "hardwood_floors"],
                "confidence_scores": {
                    "property_type": 0.9,
                    "style": 0.85,
                    "amenities": 0.8
                }
            },
            "living_room": {
                "description": "A spacious living room with hardwood floors, large windows, and a fireplace. The room appears to be in a modern apartment.",
                "property_type": "apartment",
                "rooms": {"living_room": 1, "bedroom": 2},
                "amenities": ["fireplace", "hardwood_floors"],
                "style": "modern",
                "materials": ["hardwood_floors"],
                "confidence_scores": {
                    "property_type": 0.85,
                    "style": 0.8,
                    "amenities": 0.75
                }
            },
            "bedroom": {
                "description": "A bedroom with hardwood floors and large windows. The room appears clean and well-maintained.",
                "property_type": "apartment",
                "rooms": {"bedroom": 1},
                "amenities": ["hardwood_floors", "large_window"],
                "style": "modern",
                "materials": ["hardwood_floors"],
                "confidence_scores": {
                    "property_type": 0.8,
                    "style": 0.75,
                    "amenities": 0.7
                }
            },
            "bathroom": {
                "description": "A modern bathroom with tile floors, a bathtub, and updated fixtures. The space is clean and well-lit.",
                "property_type": "apartment",
                "rooms": {"bathroom": 1},
                "amenities": ["tile_floors", "bathtub", "updated_fixtures"],
                "style": "modern",
                "materials": ["tile_floors"],
                "confidence_scores": {
                    "property_type": 0.85,
                    "style": 0.8,
                    "amenities": 0.75
                }
            },
            "dining_room": {
                "description": "A formal dining room with hardwood floors and a chandelier. The room connects to the kitchen and living areas.",
                "property_type": "house",
                "rooms": {"dining_room": 1},
                "amenities": ["hardwood_floors", "chandelier"],
                "style": "traditional",
                "materials": ["hardwood_floors"],
                "confidence_scores": {
                    "property_type": 0.8,
                    "style": 0.75,
                    "amenities": 0.7
                }
            },
            "exterior": {
                "description": "A two-story house with vinyl siding, a garage, and a small front yard. The property appears well-maintained.",
                "property_type": "house",
                "rooms": {"bedroom": 3},
                "amenities": ["garage", "garden"],
                "style": "traditional",
                "materials": ["vinyl_siding"],
                "confidence_scores": {
                    "property_type": 0.9,
                    "style": 0.8,
                    "amenities": 0.85
                }
            }
        }
    
    def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Return mock response based on image size or default."""
        try:
            # Try to parse image to get basic info
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Simple heuristic: choose mock response based on image dimensions
            if width > height * 1.5:  # Likely exterior/wide shot
                response_key = "exterior"
            elif height > width * 1.2:  # Likely tall room (kitchen/bathroom)
                # Randomly choose between kitchen and bathroom for variety
                import random
                response_key = random.choice(["kitchen", "bathroom"])
            else:  # Square-ish, likely living room, bedroom, or dining room
                # Randomly choose for more realistic variety
                import random
                response_key = random.choice(["living_room", "bedroom", "dining_room"])
            
            # Add some variation based on image size
            response = self.mock_responses[response_key].copy()
            response["image_info"] = {
                "width": width,
                "height": height,
                "format": image.format,
                "size_bytes": len(image_data)
            }
            
            # Add condition based on image size (larger images might indicate better condition)
            if len(image_data) > 50000:  # Large image
                response["condition"] = "excellent"
            elif len(image_data) > 20000:  # Medium image
                response["condition"] = "good"
            else:  # Small image
                response["condition"] = "fair"
            
            logger.info(f"MockVisionModel returning {response_key} response for {width}x{height} image")
            return response
            
        except Exception as e:
            logger.warning(f"Could not parse image, using default mock response: {e}")
            # Return a random room type instead of just living_room
            import random
            default_key = random.choice(["living_room", "bedroom", "kitchen"])
            response = self.mock_responses[default_key].copy()
            response["condition"] = "good"
            return response


class OpenAIVisionModel(VisionModelInterface):
    """OpenAI GPT-4.1 vision model implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4.1"
        except ImportError:
            raise VisionModelError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise VisionModelError(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image using OpenAI GPT-4.1."""
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Detect image format
            image = Image.open(io.BytesIO(image_data))
            image_format = image.format.lower() if image.format else "jpeg"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                # Look for JSON in the response
                if content.strip().startswith('{'):
                    result = json.loads(content)
                else:
                    # Try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(1))
                    else:
                        # Fallback: create structured response from text
                        result = self._parse_text_response(content)
                        
                result["confidence_scores"] = {
                    "property_type": 0.8,
                    "style": 0.7,
                    "amenities": 0.75
                }
                
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse JSON response, using text fallback: {e}")
                return self._parse_text_response(content)
                
        except Exception as e:
            logger.error(f"OpenAI vision model error: {e}")
            raise VisionModelError(f"Failed to analyze image: {e}")
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format."""
        from app.feature_extractor import extract_features
        
        # Extract features using the existing feature extractor
        features = extract_features(text)
        
        return {
            "description": text,
            "property_type": features["property_type"],
            "rooms": features["rooms"],
            "amenities": features["amenities"],
            "style": features["style"],
            "materials": features["materials"]
        }


class AnthropicVisionModel(VisionModelInterface):
    """Anthropic Claude vision model implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-3-sonnet-20240229"
        except ImportError:
            raise VisionModelError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise VisionModelError(f"Failed to initialize Anthropic client: {e}")
    
    def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image using Anthropic Claude."""
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Detect image format
            image = Image.open(io.BytesIO(image_data))
            image_format = image.format.lower() if image.format else "jpeg"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_format}",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Try to parse as JSON, fallback to text parsing
            try:
                if content.strip().startswith('{'):
                    result = json.loads(content)
                else:
                    # Try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```json\s*({.*?})\s*```', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(1))
                    else:
                        result = self._parse_text_response(content)
                        
                result["confidence_scores"] = {
                    "property_type": 0.8,
                    "style": 0.7,
                    "amenities": 0.75
                }
                
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse JSON response, using text fallback: {e}")
                return self._parse_text_response(content)
                
        except Exception as e:
            logger.error(f"Anthropic vision model error: {e}")
            raise VisionModelError(f"Failed to analyze image: {e}")
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format."""
        from app.feature_extractor import extract_features
        
        # Extract features using the existing feature extractor
        features = extract_features(text)
        
        return {
            "description": text,
            "property_type": features["property_type"],
            "rooms": features["rooms"],
            "amenities": features["amenities"],
            "style": features["style"],
            "materials": features["materials"]
        }


def create_vision_model(model_type: str = "mock", **kwargs) -> VisionModelInterface:
    """
    Factory function to create vision model instances.
    
    Args:
        model_type: Type of model ('mock', 'openai', 'anthropic')
        **kwargs: Additional arguments passed to model constructor
        
    Returns:
        VisionModelInterface implementation
        
    Raises:
        VisionModelError: If model type is invalid or initialization fails
    """
    if model_type == "mock":
        return MockVisionModel()
    elif model_type == "openai":
        return OpenAIVisionModel(**kwargs)
    elif model_type == "anthropic":
        return AnthropicVisionModel(**kwargs)
    else:
        raise VisionModelError(f"Unknown model type: {model_type}")


def preprocess_image(image_data: bytes, max_size: int = 1024, quality: int = 85) -> bytes:
    """
    Preprocess image for vision model analysis.
    
    Args:
        image_data: Raw image bytes
        max_size: Maximum dimension in pixels
        quality: JPEG quality (1-100)
        
    Returns:
        Processed image bytes
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if larger than max_size
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save as JPEG with quality setting
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality)
        processed_data = output.getvalue()
        
        logger.info(f"Image preprocessed: {len(image_data)} -> {len(processed_data)} bytes")
        return processed_data
        
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return image_data  # Return original if processing fails


# Default prompt for property analysis
DEFAULT_PROPERTY_PROMPT = """
You are analyzing property images for a home seller who is creating a property listing.
This analysis will help them accurately describe their property features, condition, and amenities to attract potential buyers.

Analyze this property image and provide a structured response with the following information:

1. **description**: A detailed description of what you see in the image (2-3 sentences, highlighting key features that would matter to a buyer)
2. **property_type**: The type of property (apartment, house, townhouse, condo, etc.)
3. **rooms**: Count of different room types visible (bedroom, bathroom, kitchen, living_room, dining_room, etc.)
4. **amenities**: List of amenities and features visible (pool, fireplace, balcony, garage, dishwasher, etc.)
5. **style**: Architectural style (modern, traditional, rustic, contemporary, etc.)
6. **materials**: Building materials and finishes visible (hardwood_floors, granite_counters, tile, carpet, etc.)
7. **condition**: Overall condition impression (excellent, good, fair, needs_work)

Please respond in JSON format like this example:
{
  "description": "A modern kitchen with granite countertops and stainless steel appliances. The space features ample cabinet storage and appears well-maintained. Natural lighting from a large window creates a bright atmosphere.",
  "property_type": "apartment",
  "rooms": {"kitchen": 1},
  "amenities": ["granite_counters", "stainless_steel", "dishwasher", "large_window"],
  "style": "modern",
  "materials": ["granite_counters", "stainless_steel", "tile_backsplash"],
  "condition": "excellent"
}

Be specific and accurate based only on what you can see in the image. Focus on details that would be valuable for the seller to highlight in their listing.
"""


# Global instance for convenience
_vision_model = None

def get_vision_model(model_type: str = "mock", **kwargs) -> VisionModelInterface:
    """Get or create the global vision model instance."""
    global _vision_model
    if _vision_model is None:
        _vision_model = create_vision_model(model_type, **kwargs)
    return _vision_model

def analyze_multiple_images(
    images: list[bytes],
    model_type: str = "mock",
    prompt: str = DEFAULT_PROPERTY_PROMPT,
    preprocess: bool = True,
    **model_kwargs
) -> dict[str, Any]:
    """
    Analyze multiple property images and synthesize unified results.
    
    Args:
        images: List of image data (bytes)
        model_type: Vision model to use ('mock', 'openai', 'anthropic')
        prompt: Custom prompt for the vision model
        preprocess: Whether to preprocess images
        **model_kwargs: Additional arguments passed to model constructor
        
    Returns:
        Dictionary containing individual analyses and synthesized overview
        {
            "individual_analyses": [...],  # Each image's analysis
            "synthesis": {
                "total_rooms": 6,
                "room_breakdown": {...},
                "amenities_by_room": {...},
                "unified_description": "...",
                "property_overview": {...},
                "layout_type": "open_concept",
                "exterior_features": [...]
            }
        }
        
    Raises:
        VisionModelError: If analysis fails
    """
    # Analyze each image individually
    individual_analyses = []
    
    for i, image_data in enumerate(images):
        try:
            analysis = analyze_property_image(
                image_data=image_data,
                model_type=model_type,
                prompt=prompt,
                preprocess=preprocess,
                **model_kwargs
            )
            analysis["image_index"] = i
            individual_analyses.append(analysis)
        except Exception as e:
            logger.error(f"Failed to analyze image {i}: {e}")
            # Add a minimal analysis for failed images
            individual_analyses.append({
                "image_index": i,
                "description": f"Analysis failed for image {i}",
                "property_type": "unknown",
                "rooms": {},
                "amenities": [],
                "style": "unknown",
                "materials": [],
                "condition": "unknown",
                "error": str(e)
            })
    
    # Synthesize the results
    synthesis = synthesize_property_overview(individual_analyses)
    
    return {
        "individual_analyses": individual_analyses,
        "synthesis": synthesis
    }


def synthesize_property_overview(analyses: list[dict]) -> dict:
    """
    Correlate multiple image analyses into unified property description.
    
    Args:
        analyses: List of individual image analyses
        
    Returns:
        Dictionary containing synthesized property overview
    """
    if not analyses:
        return {
            "total_rooms": 0,
            "room_breakdown": {},
            "amenities_by_room": {},
            "unified_description": "No images analyzed.",
            "property_overview": {},
            "layout_type": "unknown",
            "exterior_features": []
        }
    
    # Separate interior and exterior analyses
    interior_analyses = []
    exterior_analyses = []
    
    for analysis in analyses:
        rooms = analysis.get("rooms", {})
        # If no rooms detected, treat as exterior image
        if not rooms or sum(rooms.values()) == 0:
            exterior_analyses.append(analysis)
        else:
            interior_analyses.append(analysis)
    
    # Detect open-concept spaces in interior images
    open_concept_detected = False
    interior_amenities = set()
    interior_materials = set()
    
    # Check each interior image for open-concept layout
    for analysis in interior_analyses:
        rooms = analysis.get("rooms", {})
        room_types = list(rooms.keys())
        room_count = sum(rooms.values())
        
        # If single image has multiple room types, it's likely open-concept
        if len(room_types) >= 3 and room_count >= 3:
            open_concept_detected = True
        
        # Collect interior amenities and materials
        amenities = analysis.get("amenities", [])
        materials = analysis.get("materials", [])
        interior_amenities.update(amenities)
        interior_materials.update(materials)
    
    # Fix for open-concept counting: if detected and only 1 interior image, treat as 1 room
    property_types = []
    styles = []
    
    if open_concept_detected and len(interior_analyses) == 1:
        # Single image with multiple functional areas = open concept studio
        total_rooms = 1
        room_breakdown = {"open_concept_space": 1}
        
        # Still track what functional areas it has for description
        original_rooms = interior_analyses[0].get("rooms", {})
        functional_areas = list(original_rooms.keys())
        
        # Collect property types and styles from the single interior analysis
        if interior_analyses[0].get("property_type"):
            property_types.append(interior_analyses[0]["property_type"])
        if interior_analyses[0].get("style"):
            styles.append(interior_analyses[0]["style"])
    else:
        # Normal room counting for traditional layout or multiple images
        total_rooms = 0
        room_breakdown = {}
        
        # Aggregate room counts across interior images only
        for i, analysis in enumerate(interior_analyses):
            room_key = f"room_{i+1}"
            
            # Count rooms from this analysis
            if analysis.get("rooms"):
                for room_type, count in analysis["rooms"].items():
                    room_breakdown[room_type] = room_breakdown.get(room_type, 0) + count
                    total_rooms += count
            
            # Collect property types and styles
            if analysis.get("property_type"):
                property_types.append(analysis["property_type"])
            if analysis.get("style"):
                styles.append(analysis["style"])
    
    amenities_by_room = {}
    property_types = []
    styles = []
    
    # Handle exterior features separately
    exterior_features = []
    exterior_amenities = set()
    
    for analysis in exterior_analyses:
        amenities = analysis.get("amenities", [])
        description = analysis.get("description", "")
        
        # Add exterior-specific amenities
        exterior_amenities.update(amenities)
        
        # Extract exterior features from description if no specific amenities
        if not amenities and description:
            if any(word in description.lower() for word in ['porch', 'patio', 'deck', 'balcony']):
                exterior_features.append('outdoor living space')
            if any(word in description.lower() for word in ['garden', 'landscaped', 'yard']):
                exterior_features.append('landscaping')
            if any(word in description.lower() for word in ['garage', 'driveway']):
                exterior_features.append('parking')
    
    # Add specific exterior amenities as features
    for amenity in exterior_amenities:
        if amenity in ['garage', 'garden', 'pool', 'balcony', 'patio', 'deck', 'front_porch', 'landscaping', 'landscape']:
            exterior_features.append(amenity.replace('_', ' '))
    
    # Also add generic features if specific ones aren't found but description suggests them
    if not exterior_features and exterior_analyses:
        for analysis in exterior_analyses:
            description = analysis.get("description", "").lower()
            if any(word in description for word in ['porch', 'patio', 'deck', 'balcony']):
                if 'outdoor living space' not in exterior_features:
                    exterior_features.append('outdoor living space')
            if any(word in description for word in ['garden', 'landscaped', 'yard', 'landscaping']):
                if 'landscaping' not in exterior_features:
                    exterior_features.append('landscaping')
            if any(word in description for word in ['garage', 'driveway', 'parking']):
                if 'parking' not in exterior_features:
                    exterior_features.append('parking')
    
    # Determine layout type
    layout_type = "open_concept" if open_concept_detected else "traditional"
    
    # Determine dominant property type and style from all analyses
    all_analyses = interior_analyses + exterior_analyses
    
    # Better property type detection - prioritize from interior if available
    if property_types:
        dominant_property_type = max(set(property_types), key=property_types.count)
    elif all_analyses:
        # Fallback to any available property type
        for analysis in all_analyses:
            if analysis.get("property_type"):
                dominant_property_type = analysis["property_type"]
                break
        else:
            dominant_property_type = "unknown"
    else:
        dominant_property_type = "unknown"
    
    if styles:
        dominant_style = max(set(styles), key=styles.count)
    elif all_analyses:
        # Fallback to any available style
        for analysis in all_analyses:
            if analysis.get("style"):
                dominant_style = analysis["style"]
                break
        else:
            dominant_style = "unknown"
    else:
        dominant_style = "unknown"
    
    # Generate unified description
    unified_description = generate_unified_description(
        total_rooms=total_rooms,
        room_breakdown=room_breakdown,
        amenities=list(interior_amenities),
        materials=list(interior_materials),
        property_type=dominant_property_type,
        style=dominant_style,
        analyses=all_analyses,
        layout_type=layout_type,
        exterior_features=exterior_features,
        open_concept_detected=open_concept_detected,
        interior_analyses=interior_analyses
    )
    
    # Create property overview
    property_overview = {
        "property_type": dominant_property_type,
        "style": dominant_style,
        "total_rooms": total_rooms,
        "room_breakdown": room_breakdown,
        "common_amenities": list(interior_amenities),
        "common_materials": list(interior_materials),
        "condition": determine_overall_condition(all_analyses)
    }
    
    return {
        "total_rooms": total_rooms,
        "room_breakdown": room_breakdown,
        "amenities_by_room": amenities_by_room,
        "unified_description": unified_description,
        "property_overview": property_overview,
        "layout_type": layout_type,
        "interior_features": list(interior_amenities),
        "exterior_features": list(set(exterior_features))
    }


def generate_unified_description(
    total_rooms: int,
    room_breakdown: dict,
    amenities: list,
    materials: list,
    property_type: str,
    style: str,
    analyses: list[dict],
    layout_type: str = "traditional",
    exterior_features: list = None,
    open_concept_detected: bool = False,
    interior_analyses: list = None
) -> str:
    """
    Generate a coherent unified description from multiple analyses.
    
    Args:
        total_rooms: Total number of rooms
        room_breakdown: Dictionary of room types and counts
        amenities: List of all amenities found
        materials: List of all materials found
        property_type: Dominant property type
        style: Dominant style
        analyses: Original individual analyses
        layout_type: "open_concept" or "traditional"
        exterior_features: List of exterior features
        
    Returns:
        Unified description string
    """
    if total_rooms == 0 and not exterior_features:
        return "No rooms detected in the provided images."
    
    # Build room description
    room_parts = []
    for room_type, count in sorted(room_breakdown.items()):
        if count > 0:
            room_name = room_type.replace("_", " ").title()
            if count == 1:
                room_parts.append(f"1 {room_name}")
            else:
                room_parts.append(f"{count} {room_name}s")
    
    room_description = ", ".join(room_parts)
    
    # Special handling for open-concept to show functional areas
    if layout_type == "open_concept" and open_concept_detected and len(interior_analyses) == 1:
        # Show the functional areas instead of just "Open Concept Space"
        original_rooms = interior_analyses[0].get("rooms", {})
        functional_areas = []
        for room_type, count in original_rooms.items():
            room_name = room_type.replace("_", " ").title()
            functional_areas.append(room_name)
        if functional_areas:
            room_description = ", ".join(functional_areas)
    
    # Build amenities description
    amenity_descriptions = []
    
    # Check for common patterns
    if "hardwood_floors" in materials and sum(1 for a in analyses if "hardwood_floors" in a.get("amenities", [])) > len(analyses) / 2:
        amenity_descriptions.append("hardwood floors throughout")
    
    if "granite_counters" in amenities:
        amenity_descriptions.append("granite countertops")
    
    if "stainless_steel" in amenities:
        amenity_descriptions.append("stainless steel appliances")
    
    if "fireplace" in amenities:
        amenity_descriptions.append("fireplace")
    
    if "dishwasher" in amenities:
        amenity_descriptions.append("dishwasher")
    
    # Add other notable amenities
    other_amenities = [a for a in amenities if a not in ["hardwood_floors", "granite_counters", "stainless_steel", "fireplace", "dishwasher"]]
    if other_amenities:
        # Pick a few more to mention
        notable = [a.replace("_", " ") for a in other_amenities[:2]]
        amenity_descriptions.extend(notable)
    
    # Build final description based on layout type
    if layout_type == "open_concept":
        if total_rooms == 1:
            description = f"This {property_type} has 1 open-concept space"
        elif total_rooms == 0:
            description = f"This {property_type} features an open-concept design"
        else:
            description = f"This {property_type} has an open-concept layout with {total_rooms} distinct area{'s' if total_rooms != 1 else ''}"
    else:
        if total_rooms == 0:
            description = f"This {property_type}"
        elif total_rooms == 1:
            description = f"This {property_type} has 1 room"
        else:
            description = f"This {property_type} has {total_rooms} rooms"
    
    if room_description:
        if layout_type == "open_concept":
            description += f" including {room_description}"
        else:
            description += f": {room_description}"
    
    if amenity_descriptions:
        description += f". Features include {', '.join(amenity_descriptions)}"
    
    # Add exterior features if present
    if exterior_features:
        description += f". Exterior features include {', '.join(exterior_features)}"
    
    if style and style != "unknown":
        description += f". Overall style: {style}"
    
    description += "."
    
    return description


def determine_overall_condition(analyses: list[dict]) -> str:
    """
    Determine the overall condition from multiple analyses.
    
    Args:
        analyses: List of individual analyses
        
    Returns:
        Overall condition string
    """
    conditions = [analysis.get("condition", "unknown") for analysis in analyses]
    
    # Count condition frequencies
    condition_counts = {}
    for condition in conditions:
        condition_counts[condition] = condition_counts.get(condition, 0) + 1
    
    # Return the most common condition, or "mixed" if varied
    if len(condition_counts) == 1:
        return list(condition_counts.keys())[0]
    elif len(condition_counts) > 1:
        return "mixed"
    else:
        return "unknown"


def analyze_property_image(image_data: bytes, model_type: str = "mock", 
                          prompt: str = DEFAULT_PROPERTY_PROMPT, 
                          preprocess: bool = True,
                          **model_kwargs) -> Dict[str, Any]:
    """
    Convenience function to analyze a property image.
    
    Args:
        image_data: Raw image bytes
        model_type: Type of model to use ('mock', 'openai', 'anthropic')
        prompt: Custom prompt for the vision model
        preprocess: Whether to preprocess the image
        **model_kwargs: Additional arguments passed to model constructor (e.g., api_key)
        
    Returns:
        Dictionary containing analyzed property data
        
    Raises:
        VisionModelError: If analysis fails
    """
    # Preprocess image if requested
    if preprocess:
        image_data = preprocess_image(image_data)
    
    # Create vision model directly with kwargs instead of using global instance
    vision_model = create_vision_model(model_type, **model_kwargs)
    return vision_model.analyze_image(image_data, prompt)
