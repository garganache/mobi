# TASK-038: Update Frontend Components with Romanian Text

**Story:** STORY-008 (Romanian Localization)
**Status:** todo
**Priority:** high
**Assigned:** -
**Effort:** 4 hours
**Depends on:** TASK-037

## Objective

Replace all hardcoded English text in frontend components with translation function calls.

## Files to Update

### 1. App.svelte

**Replace:**
```svelte
<button>Continue</button>
<button>Preview & Save</button>
<button>Reset form</button>
```

**With:**
```svelte
<script>
  import { t } from '$lib/i18n';
</script>

<button>{t('button.continue')}</button>
<button>{t('button.preview_save')}</button>
<button>{t('button.reset')}</button>
```

### 2. ImageUpload.svelte

**Replace:**
```svelte
"Drop a photo to start your listing"
"Get Started"
"Upload"
```

**With:**
```svelte
{t('message.drop_photo')}
{t('button.start')}
{t('button.upload')}
```

### 3. AnimatedDynamicForm.svelte

**Update field labels:**
```svelte
<script>
  import { t } from '$lib/i18n';
  
  // Map field IDs to Romanian labels
  function getFieldLabel(fieldId: string): string {
    return t(`field.${fieldId}`);
  }
</script>

<label>{getFieldLabel(field.id)}</label>
```

### 4. SynthesisDisplay.svelte

**Replace:**
```svelte
"Property Overview"
"images analyzed"
"Rooms detected in images:"
```

**With:**
```svelte
{t('header.property_overview')}
{t('message.images_analyzed')}
{t('message.rooms_detected')}
```

**Update room names:**
```svelte
<script>
  import { getRoomLabel } from '$lib/i18n';
  
  function formatRoomName(roomType: string): string {
    return getRoomLabel(roomType);
  }
</script>
```

### 5. ListingPreview.svelte

**Replace:**
```svelte
"Preview Listing"
"Check all the details of your listing"
"Save Listing"
"Edit"
```

**With:**
```svelte
{t('header.preview_listing')}
{t('message.check_details')}
{t('button.save')}
{t('button.edit')}
```

### 6. SuccessModal.svelte (if exists)

**Replace:**
```svelte
"Listing saved successfully"
"Create Another Listing"
"View Listing"
```

**With:**
```svelte
{t('message.listing_saved')}
{t('button.create_another')}
{t('button.view_listing')}
```

## Property Type Dropdown

**Update options to show Romanian labels:**

```svelte
<script>
  import { getPropertyTypeLabel } from '$lib/i18n';
  
  const propertyTypeOptions = [
    { value: 'apartment', label: getPropertyTypeLabel('apartment') },
    { value: 'house', label: getPropertyTypeLabel('house') },
    { value: 'condo', label: getPropertyTypeLabel('condo') },
    { value: 'townhouse', label: getPropertyTypeLabel('townhouse') },
    { value: 'land', label: getPropertyTypeLabel('land') },
    { value: 'commercial', label: getPropertyTypeLabel('commercial') }
  ];
</script>

<select bind:value={selectedType}>
  {#each propertyTypeOptions as option}
    <option value={option.value}>{option.label}</option>
  {/each}
</select>
```

## Error Messages

**Replace all validation messages:**

```typescript
// Before
if (!propertyType) {
  error = "Please select a property type before previewing";
}

// After
import { t } from '$lib/i18n';

if (!propertyType) {
  error = t('error.property_type_required');
}
```

## Acceptance Criteria

- [ ] All visible text uses translation function
- [ ] No hardcoded English text remains
- [ ] Property type dropdown shows Romanian labels
- [ ] Field labels are in Romanian
- [ ] Button text is in Romanian
- [ ] Error messages are in Romanian
- [ ] Room names display in Romanian
- [ ] Amenity names display in Romanian
- [ ] App builds without errors
- [ ] Visual regression test passes

## Testing Checklist

- [ ] Open app - all text in Romanian
- [ ] Upload image - messages in Romanian
- [ ] See form - labels in Romanian
- [ ] Click buttons - text in Romanian
- [ ] See errors - messages in Romanian
- [ ] Property type dropdown - options in Romanian
- [ ] Preview page - all text in Romanian
- [ ] Success modal - text in Romanian

## Notes

- Import translation functions at top of each component
- Use helper functions for dynamic content (room names, etc.)
- Keep internal values in English (e.g., value="apartment")
- Test each component individually after updating
