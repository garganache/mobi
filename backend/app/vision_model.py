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
                "amenities": ["hardwood_floors"],
                "style": "modern",
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
            elif height > width * 1.2:  # Likely tall room
                response_key = "kitchen"
            else:  # Square-ish, likely living room or bedroom
                response_key = "living_room"
            
            # Add some variation based on image size
            response = self.mock_responses[response_key].copy()
            response["image_info"] = {
                "width": width,
                "height": height,
                "format": image.format,
                "size_bytes": len(image_data)
            }
            
            logger.info(f"MockVisionModel returning {response_key} response for {width}x{height} image")
            return response
            
        except Exception as e:
            logger.warning(f"Could not parse image, using default mock response: {e}")
            return self.mock_responses["living_room"]


class OpenAIVisionModel(VisionModelInterface):
    """OpenAI GPT-4V vision model implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4-vision-preview"
        except ImportError:
            raise VisionModelError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise VisionModelError(f"Failed to initialize OpenAI client: {e}")
    
    def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image using OpenAI GPT-4V."""
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
You are analyzing property images for a home seller who is trying to sell his property.
This analysis will help them understand the property features, condition, and amenities to make an informed buying decision.

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

Be specific and accurate based only on what you can see in the image. Focus on details that would be important to a potential buyer.
"""


# Global instance for convenience
_vision_model = None

def get_vision_model(model_type: str = "mock", **kwargs) -> VisionModelInterface:
    """Get or create the global vision model instance."""
    global _vision_model
    if _vision_model is None:
        _vision_model = create_vision_model(model_type, **kwargs)
    return _vision_model

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
