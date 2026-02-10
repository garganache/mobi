# TASK-039: Backend Romanian AI Messages

**Story:** STORY-008 (Romanian Localization)
**Status:** done
**Priority:** high
**Assigned:** -
**Effort:** 3 hours

## Objective

Modify backend to generate AI guidance messages and property descriptions in Romanian.

## Files to Update

### 1. orchestrator.py - AI Guidance Messages

**File:** `backend/app/orchestrator.py`

**Update `_generate_ai_message()` method:**

```python
def _generate_ai_message(self, current_data: Dict, step: int) -> str:
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
```

### 2. vision_model.py - Property Descriptions

**File:** `backend/app/vision_model.py`

**Update `generate_unified_description()` to return Romanian:**

```python
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
    Generate Romanian property description.
    """
    if total_rooms == 0 and not exterior_features:
        return "Nu au fost detectate camere în imaginile furnizate."
    
    # Translate property type
    property_type_ro = _translate_property_type(property_type)
    
    # Build room description (types only, no counts)
    room_types = []
    for room_type in sorted(room_breakdown.keys()):
        room_name_ro = _translate_room_type(room_type)
        room_types.append(room_name_ro)
    
    room_description = ", ".join(room_types)
    
    # Build amenities description
    amenity_descriptions_ro = []
    
    if "hardwood_floors" in materials:
        amenity_descriptions_ro.append("parchet")
    if "granite_counters" in amenities:
        amenity_descriptions_ro.append("blat de granit")
    if "stainless_steel" in amenities:
        amenity_descriptions_ro.append("aparate din oțel inoxidabil")
    if "fireplace" in amenities:
        amenity_descriptions_ro.append("șemineu")
    if "dishwasher" in amenities:
        amenity_descriptions_ro.append("mașină de spălat vase")
    
    # Build final description
    if layout_type == "open_concept":
        description = f"Acest {property_type_ro} prezintă un design open-concept"
        if room_description:
            description += f" cu zone de {room_description}"
    else:
        if room_description:
            description = f"Acest {property_type_ro} include {room_description}"
        else:
            description = f"Acest {property_type_ro}"
    
    if amenity_descriptions_ro:
        description += f". Caracteristici includ {', '.join(amenity_descriptions_ro)}"
    
    # Add exterior features
    if exterior_features:
        exterior_ro = [_translate_feature(f) for f in exterior_features]
        description += f". Caracteristici exterioare includ {', '.join(exterior_ro)}"
    
    # Add style
    if style and style != "unknown":
        style_ro = _translate_style(style)
        description += f". Stil general: {style_ro}"
    
    description += "."
    
    return description

def _translate_property_type(property_type: str) -> str:
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

def _translate_room_type(room_type: str) -> str:
    """Translate room type to Romanian."""
    translations = {
        'bedroom': 'Dormitor',
        'kitchen': 'Bucătărie',
        'living_room': 'Sufragerie',
        'bathroom': 'Baie',
        'hallway': 'Hol',
        'dining_room': 'Cameră de Mâncare',
        'office': 'Birou',
        'balcony': 'Balcon',
        'open_concept_space': 'Spațiu Open-Concept'
    }
    return translations.get(room_type, room_type.replace('_', ' ').title())

def _translate_feature(feature: str) -> str:
    """Translate exterior feature to Romanian."""
    translations = {
        'balcony': 'balcon',
        'garage': 'garaj',
        'garden': 'grădină',
        'pool': 'piscină',
        'patio': 'patio',
        'deck': 'terasă',
        'outdoor living space': 'spațiu de locuit în aer liber',
        'landscaping': 'peisagistică',
        'parking': 'parcare'
    }
    return translations.get(feature.lower(), feature)

def _translate_style(style: str) -> str:
    """Translate style to Romanian."""
    translations = {
        'modern': 'modern',
        'traditional': 'tradițional',
        'contemporary': 'contemporan',
        'rustic': 'rustic',
        'industrial': 'industrial',
        'minimalist': 'minimalist'
    }
    return translations.get(style.lower(), style)
```

## Example Output

**Before (English):**
```
This apartment includes Bedroom, Kitchen, Bathroom. Features include hardwood floors, granite countertops. Overall style: modern.
```

**After (Romanian):**
```
Acest apartament include Dormitor, Bucătărie, Baie. Caracteristici includ parchet, blat de granit. Stil general: modern.
```

## Acceptance Criteria

- [ ] AI guidance messages in Romanian
- [ ] Property descriptions in Romanian
- [ ] Property types translated correctly
- [ ] Room types translated correctly
- [ ] Amenities translated correctly
- [ ] Styles translated correctly
- [ ] Grammar is natural and correct
- [ ] Backend tests still pass
- [ ] API returns Romanian text

## Testing

```bash
# Test orchestrator messages
curl -X POST http://localhost:8000/api/analyze-step \
  -H "Content-Type: application/json" \
  -d '{"property_type": "apartment", "step": 1}'

# Expected response includes:
# "ai_message": "Excelent! Am identificat că este vorba despre un apartament..."
```

## Notes

- Keep translation dictionaries in the same file for now
- Can extract to separate translation file later if needed
- Use natural Romanian phrasing, not literal translations
- Get native speaker review before final merge
- Ensure proper Romanian diacritics (ă, â, î, ș, ț)
