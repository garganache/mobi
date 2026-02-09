"""
Pydantic schemas for the Mobi AI-guided listing system.

This module defines the UI Manifest schema that serves as the contract
between the backend and frontend for dynamic form rendering.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class FieldOption(BaseModel):
    """Option for select-type fields"""
    value: str
    label: str


class UIField(BaseModel):
    """
    Single field definition in the UI schema.
    
    The frontend's component registry will map `component_type` to
    the appropriate Svelte component.
    """
    id: str = Field(..., description="Unique identifier for this field")
    component_type: Literal['text', 'select', 'number', 'toggle'] = Field(
        ..., 
        description="Type of input component to render"
    )
    label: str = Field(..., description="Human-readable label for the field")
    placeholder: Optional[str] = Field(None, description="Placeholder text for input")
    options: Optional[list[FieldOption]] = Field(
        None, 
        description="Options for select-type fields"
    )
    min: Optional[float] = Field(None, description="Minimum value for number inputs")
    max: Optional[float] = Field(None, description="Maximum value for number inputs")
    step: Optional[float] = Field(None, description="Step increment for number inputs")
    required: bool = Field(default=False, description="Whether this field is required")
    default: Optional[Any] = Field(None, description="Default value for the field")


class UIManifest(BaseModel):
    """
    Complete UI manifest returned by /api/analyze-step.
    
    This tells the frontend:
    1. What data has been extracted/inferred so far
    2. What fields to display next
    3. What AI message to show to guide the user
    
    Example:
    ```json
    {
      "extracted_data": {
        "property_type": "apartment",
        "has_pool": false,
        "bedrooms": 3
      },
      "ui_schema": [
        {
          "id": "pool_type",
          "component_type": "select",
          "label": "Pool System Type",
          "options": [
            {"value": "salt", "label": "Salt Water"},
            {"value": "chlorine", "label": "Chlorine"}
          ],
          "required": false
        }
      ],
      "ai_message": "I noticed a pool in the image. What type of pool system does it have?"
    }
    ```
    """
    extracted_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of data extracted/inferred by AI"
    )
    ui_schema: list[UIField] = Field(
        default_factory=list,
        description="Array of field definitions for the frontend to render"
    )
    ai_message: Optional[str] = Field(
        None,
        description="Conversational message from AI to guide the user"
    )
    confidence_scores: Optional[dict[str, float]] = Field(
        None,
        description="Optional confidence scores for extracted data (0.0 - 1.0)"
    )


class AnalyzeStepRequest(BaseModel):
    """
    Request payload for /api/analyze-step endpoint.
    
    The orchestrator receives:
    - current_data: What the user has entered so far
    - new_input: New information (image URL, text, or field update)
    - input_type: What kind of input this is
    """
    current_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Current form state (field_id: value pairs)"
    )
    new_input: Optional[str] = Field(
        None,
        description="New input: base64 image, text snippet, or null if just a field update"
    )
    input_type: Literal['image', 'text', 'field_update'] = Field(
        ...,
        description="Type of new input being provided"
    )
    image_url: Optional[str] = Field(
        None,
        description="Alternative to new_input: URL of an uploaded image"
    )


class AnalyzeStepResponse(UIManifest):
    """
    Response from /api/analyze-step.
    
    Inherits from UIManifest and may add additional orchestrator-specific fields.
    """
    step_number: Optional[int] = Field(
        None,
        description="Current step in the listing creation flow"
    )
    completion_percentage: Optional[float] = Field(
        None,
        description="Estimated completion percentage (0-100)"
    )
