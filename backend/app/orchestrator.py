"""
Orchestration logic for determining which fields to show next in the AI-guided listing flow.

This module implements the "brain" that decides what questions to ask based on the current form state.
"""

from typing import Optional, Dict, Any
from app.schemas import UIField, FieldOption, AnalyzeStepResponse


# Define field configurations for different property types
PROPERTY_TYPE_FIELDS = {
    "house": [
        {
            "id": "lot_size",
            "component_type": "number",
            "label": "Lot Size (sq ft)",
            "min": 0,
            "max": 100000,
            "step": 100,
            "required": False,
        },
        {
            "id": "roof_age",
            "component_type": "number", 
            "label": "Roof Age (years)",
            "min": 0,
            "max": 100,
            "required": False,
        },
        {
            "id": "garage",
            "component_type": "select",
            "label": "Garage Type",
            "options": [
                FieldOption(value="none", label="No Garage"),
                FieldOption(value="attached", label="Attached"),
                FieldOption(value="detached", label="Detached"),
                FieldOption(value="carport", label="Carport"),
            ],
            "required": False,
        },
        {
            "id": "stories",
            "component_type": "number",
            "label": "Number of Stories",
            "min": 1,
            "max": 10,
            "default": 1,
            "required": False,
        }
    ],
    "apartment": [
        {
            "id": "floor_number",
            "component_type": "number",
            "label": "Floor Number",
            "min": 1,
            "max": 100,
            "required": False,
        },
        {
            "id": "elevator",
            "component_type": "toggle",
            "label": "Has Elevator",
            "required": False,
        },
        {
            "id": "building_age",
            "component_type": "number",
            "label": "Building Age (years)",
            "min": 0,
            "max": 200,
            "required": False,
        },
        {
            "id": "pets_allowed",
            "component_type": "toggle",
            "label": "Pets Allowed",
            "required": False,
        }
    ],
    "condo": [
        {
            "id": "condo_fees",
            "component_type": "number",
            "label": "Monthly Condo Fees",
            "min": 0,
            "max": 10000,
            "step": 50,
            "required": False,
        },
        {
            "id": "amenities",
            "component_type": "select",
            "label": "Building Amenities",
            "options": [
                FieldOption(value="gym", label="Gym/Fitness"),
                FieldOption(value="pool", label="Swimming Pool"),
                FieldOption(value="concierge", label="Concierge"),
                FieldOption(value="parking", label="Parking"),
                FieldOption(value="storage", label="Storage"),
            ],
            "required": False,
        }
    ]
}

# Common fields that apply to all property types
COMMON_FIELDS = [
    {
        "id": "bedrooms",
        "component_type": "number",
        "label": "Number of Bedrooms",
        "min": 0,
        "max": 20,
        "default": 2,
        "required": True,
        "priority": 1,
    },
    {
        "id": "bathrooms",
        "component_type": "number",
        "label": "Number of Bathrooms",
        "min": 0,
        "max": 10,
        "default": 1,
        "required": True,
        "priority": 2,
    },
    {
        "id": "square_feet",
        "component_type": "number",
        "label": "Square Feet",
        "min": 100,
        "max": 50000,
        "step": 50,
        "required": True,
        "priority": 3,
    },
    {
        "id": "price",
        "component_type": "number",
        "label": "Price",
        "min": 50000,
        "max": 10000000,
        "step": 1000,
        "required": True,
        "priority": 4,
    },
    {
        "id": "address",
        "component_type": "text",
        "label": "Address",
        "placeholder": "123 Main St, City, State",
        "required": True,
        "priority": 5,
    },
    {
        "id": "description",
        "component_type": "text",
        "label": "Description",
        "placeholder": "Describe your property...",
        "required": False,
        "priority": 6,
    },
    {
        "id": "has_parking",
        "component_type": "toggle",
        "label": "Has Parking",
        "required": False,
        "priority": 7,
    },
    {
        "id": "has_pool",
        "component_type": "toggle",
        "label": "Has Pool",
        "required": False,
        "priority": 8,
    }
]


class FieldOrchestrator:
    """
    Orchestrates which fields to show next based on current form state and property type.
    """
    
    def __init__(self):
        self.max_fields_per_step = 3
    
    def get_next_fields(self, current_data: Dict[str, Any]) -> list[UIField]:
        """
        Determine which fields to show next based on current form state.
        
        Args:
            current_data: Dictionary of current form values (field_id: value)
            
        Returns:
            List of UIField objects to display next (max 3 fields)
        """
        # If property_type is missing, it should be the first field
        if "property_type" not in current_data:
            return [
                UIField(
                    id="property_type",
                    component_type="select",
                    label="Tipul Proprietății",
                    placeholder="Selectați tipul proprietății",
                    options=[
                        FieldOption(value="house", label="Casă"),
                        FieldOption(value="apartment", label="Apartament"),
                        FieldOption(value="condo", label="Condominium"),
                        FieldOption(value="townhouse", label="Casă în Șir"),
                        FieldOption(value="land", label="Teren"),
                        FieldOption(value="commercial", label="Comercial"),
                    ],
                    required=True,
                )
            ]
        
        property_type = current_data.get("property_type")
        
        # Get fields that haven't been filled yet
        unfilled_fields = self._get_unfilled_fields(current_data, property_type)
        
        # Prioritize fields and limit to max_fields_per_step
        prioritized_fields = self._prioritize_fields(unfilled_fields, current_data)
        
        # Convert to UIField objects
        ui_fields = []
        for field_config in prioritized_fields[:self.max_fields_per_step]:
            ui_field = UIField(**field_config)
            ui_fields.append(ui_field)
        
        return ui_fields
    
    def _get_unfilled_fields(self, current_data: Dict[str, Any], property_type: Optional[str]) -> list[Dict[str, Any]]:
        """
        Get all fields that haven't been filled in the current data.
        """
        unfilled_fields = []
        
        # Get property-specific fields
        if property_type in PROPERTY_TYPE_FIELDS:
            property_fields = PROPERTY_TYPE_FIELDS[property_type]
            for field in property_fields:
                if field["id"] not in current_data:
                    unfilled_fields.append(field)
        
        # Get common fields that haven't been filled
        for field in COMMON_FIELDS:
            if field["id"] not in current_data:
                unfilled_fields.append(field)
        
        return unfilled_fields
    
    def _prioritize_fields(self, unfilled_fields: list[Dict[str, Any]], current_data: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Prioritize fields based on importance and current form state.
        """
        # Add priority to fields that don't have it
        for field in unfilled_fields:
            if "priority" not in field:
                field["priority"] = 10  # Default priority for non-essential fields
        
        # Sort by priority (lower number = higher priority)
        return sorted(unfilled_fields, key=lambda x: x["priority"])
    
    def generate_ai_message(self, current_data: Dict[str, Any], next_fields: list[UIField]) -> str:
        """
        Generate an appropriate AI message based on the current state and next fields.
        """
        return self._generate_ai_message(current_data, len(current_data))
    
    def _generate_ai_message(self, current_data: Dict[str, Any], step: int) -> str:
        """Generate Romanian AI guidance message based on current state."""
        
        # No property type yet
        if not current_data.get("property_type"):
            return "Să începem prin a identifica ce tip de proprietate afișați."
        
        property_type_ro = self._translate_property_type(current_data.get("property_type"))
        
        # Early steps
        if step < 3:
            return f"Excelent! Am identificat că este vorba despre un {property_type_ro}. Să continuăm cu detaliile esențiale."
        
        # Middle steps
        if step < 5:
            return "Faceți progrese bune! Încă câteva detalii cheie pentru anunțul dvs."
        
        # Later steps
        if step < 7:
            return "Aproape gata! Permiteți-mi să completez informațiile finale."
        
        # Complete
        return "Perfect! Ați completat toate informațiile necesare. Sunteți gata să previzualizați și să salvați anunțul?"

    def _translate_property_type(self, property_type: str) -> str:
        """Translate property type to Romanian."""
        translations = {
            'apartment': 'apartament',
            'house': 'casă',
            'condo': 'condominium',
            'townhouse': 'casă în șir',
            'land': 'teren',
            'commercial': 'proprietate comercială'
        }
        return translations.get(property_type, property_type)
    
    def calculate_completion_percentage(self, current_data: Dict[str, Any]) -> float:
        """
        Calculate estimated completion percentage based on fields filled.
        """
        # Count total possible fields (common + property-specific)
        property_type = current_data.get("property_type")
        total_fields = len(COMMON_FIELDS)
        
        if property_type in PROPERTY_TYPE_FIELDS:
            total_fields += len(PROPERTY_TYPE_FIELDS[property_type])
        
        # Calculate percentage
        filled_fields = len(current_data)
        if total_fields == 0:
            return 0.0
        
        percentage = (filled_fields / total_fields) * 100
        return min(percentage, 100.0)


# Global orchestrator instance
orchestrator = FieldOrchestrator()