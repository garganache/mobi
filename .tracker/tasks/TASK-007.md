# TASK-007: Design and document UI manifest JSON schema

**Story:** STORY-003
**Status:** done
**Priority:** high
**Estimated:** 1h

## Description

Design the JSON schema for the "UI Manifest" that the backend returns to tell the frontend what to render. This schema is the contract between backend and frontend, so it needs to be well-documented and extensible.

## Schema Structure

```json
{
  "extracted_data": {
    "property_type": "apartment",
    "has_pool": false
  },
  "ui_schema": [
    {
      "component_type": "select",
      "id": "pool_type",
      "label": "Pool System Type",
      "options": ["Salt", "Chlorine"],
      "required": false
    }
  ],
  "ai_message": "I see a beautiful kitchen! Could you tell me more about the property?"
}
```

## Definition of Done

- [x] JSON schema structure documented
- [x] Field definitions for all properties explained
- [x] Example manifests created for different scenarios
- [x] Schema added to API documentation
- [x] Validation rules defined (e.g., required fields)
- [x] TypeScript types created (if using TypeScript)
