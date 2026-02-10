# TASK-040: Update Property Type Dropdown Options

**Story:** STORY-008 (Romanian Localization)
**Status:** in_progress
**Priority:** medium
**Assigned:** -
**Effort:** 1 hour
**Depends on:** TASK-037

## Objective

Update the property type dropdown to display Romanian labels while keeping English values for backend/database.

## Implementation

### Location

**File:** `frontend/src/App.svelte` (where property_type field is injected)

### Current Code

```typescript
schema = [
  {
    id: 'property_type',
    type: 'select',
    label: 'Property Type',
    required: true,
    options: [
      { value: 'apartment', label: 'Apartment' },
      { value: 'house', label: 'House' },
      { value: 'condo', label: 'Condo' },
      { value: 'townhouse', label: 'Townhouse' },
      { value: 'land', label: 'Land' },
      { value: 'commercial', label: 'Commercial' }
    ]
  },
  ...schema
];
```

### Updated Code

```typescript
import { t, getPropertyTypeLabel } from '$lib/i18n';

// When injecting property_type field
schema = [
  {
    id: 'property_type',
    type: 'select',
    label: t('field.property_type'), // "Tipul Proprietății"
    required: true,
    options: [
      { value: 'apartment', label: getPropertyTypeLabel('apartment') }, // "Apartament"
      { value: 'house', label: getPropertyTypeLabel('house') },         // "Casă"
      { value: 'condo', label: getPropertyTypeLabel('condo') },         // "Condominium"
      { value: 'townhouse', label: getPropertyTypeLabel('townhouse') }, // "Casă în Șir"
      { value: 'land', label: getPropertyTypeLabel('land') },           // "Teren"
      { value: 'commercial', label: getPropertyTypeLabel('commercial') } // "Comercial"
    ]
  },
  ...schema
];
```

## What User Sees

**Dropdown label:** "Tipul Proprietății"

**Dropdown options:**
```
[ Selectează ▼ ]
  Apartament
  Casă
  Condominium
  Casă în Șir
  Teren
  Comercial
```

## What Backend Receives

**When user selects "Apartament", backend gets:**
```json
{
  "property_type": "apartment"
}
```

The English value is sent to the API and stored in the database.

## Also Update Backend Schema (if needed)

If backend sends property_type in ui_schema, update it to include Romanian labels:

**File:** `backend/app/orchestrator.py`

```python
def _get_property_type_field(self) -> Dict:
    """Get property type field with Romanian labels."""
    return {
        "id": "property_type",
        "type": "select",
        "label": "Tipul Proprietății",
        "required": True,
        "options": [
            {"value": "apartment", "label": "Apartament"},
            {"value": "house", "label": "Casă"},
            {"value": "condo", "label": "Condominium"},
            {"value": "townhouse", "label": "Casă în Șir"},
            {"value": "land", "label": "Teren"},
            {"value": "commercial", "label": "Comercial"}
        ]
    }
```

## Blocker
Cannot proceed with TASK-040 until TASK-037 (Create i18n Infrastructure) is completed. TASK-040 depends on the translation helpers (`t`, `getPropertyTypeLabel`) that will be created in TASK-037.

## Implementation

The i18n infrastructure from TASK-037 is now complete. The translation helpers are available at `frontend/src/lib/i18n/index.ts`.

## Acceptance Criteria

- [ ] Dropdown label shows "Tipul Proprietății"
- [ ] Options display Romanian labels
- [ ] Selecting "Apartament" sends `property_type: "apartment"` to backend
- [ ] Database stores English value ("apartment")
- [ ] Preview page shows Romanian label
- [ ] No breaking changes to API contract
- [ ] All existing tests pass

## Testing

1. **Manual test:**
   - Open app
   - Upload images
   - See dropdown: "Tipul Proprietății"
   - Open dropdown - see Romanian options
   - Select "Apartament"
   - Check browser DevTools Network tab - POST body contains `"property_type": "apartment"`
   - Continue to preview - see "Apartament" displayed

2. **E2E test:**
```typescript
await page.selectOption('select[name="property_type"]', 'apartment');
await expect(page.locator('select[name="property_type"]')).toHaveValue('apartment');
// Verify label shows Romanian
await expect(page.locator('label[for="property_type"]')).toHaveText('Tipul Proprietății');
```

## Notes

- **Critical:** Keep `value` in English, only change `label`
- This maintains API compatibility
- Database remains language-independent
- Easy to add more languages later (just add more label translations)
