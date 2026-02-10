# TASK-041: Translate Error and Validation Messages

**Story:** STORY-008 (Romanian Localization)
**Status:** todo
**Priority:** medium
**Assigned:** -
**Effort:** 2 hours
**Depends on:** TASK-037

## Objective

Replace all error messages, validation messages, and user confirmations with Romanian translations.

## Files to Update

### 1. App.svelte - Main Error Messages

**Replace validation errors:**

```typescript
import { t } from '$lib/i18n';

// Property type validation
if (!currentData.property_type) {
  error = t('error.property_type_required');
  // "Selectați tipul proprietății înainte de previzualizare"
  return;
}

// Images validation
if (uploadedImages.length === 0) {
  error = t('error.images_required');
  // "Este necesară cel puțin o imagine"
  return;
}

// Save error
if (!saveResponse.ok) {
  error = t('error.save_failed');
  // "Nu s-a putut salva anunțul"
  return;
}
```

### 2. Confirmation Dialogs

**Reset form confirmation:**

```typescript
// Before
const confirmed = confirm("Are you sure you want to reset the form? This will clear all data.");

// After
const message = `${t('confirm.reset_form')}\n${t('confirm.clear_data')}`;
const confirmed = confirm(message);
// "Sigur doriți să resetați formularul?\nToate datele vor fi șterse."
```

### 3. AnimatedDynamicForm.svelte - Field Validation

**Add field-level validation messages:**

```typescript
function validateField(field: any, value: any): string | null {
  if (field.required && !value) {
    return t('error.field_required', { field: t(`field.${field.id}`) });
    // "Câmpul {field} este obligatoriu"
  }
  
  if (field.type === 'number' && isNaN(value)) {
    return t('error.invalid_number');
    // "Introduceți un număr valid"
  }
  
  if (field.type === 'email' && !isValidEmail(value)) {
    return t('error.invalid_email');
    // "Adresa de email nu este validă"
  }
  
  return null;
}
```

### 4. Additional Error Messages in i18n

**Update `frontend/src/lib/i18n/index.ts`:**

```typescript
export const translations = {
  ro: {
    // ... existing translations ...
    
    // Error messages
    'error.property_type_required': 'Selectați tipul proprietății înainte de previzualizare',
    'error.images_required': 'Este necesară cel puțin o imagine',
    'error.invalid_price': 'Prețul trebuie să fie un număr valid',
    'error.save_failed': 'Nu s-a putut salva anunțul',
    'error.field_required': 'Acest câmp este obligatoriu',
    'error.invalid_number': 'Introduceți un număr valid',
    'error.invalid_email': 'Adresa de email nu este validă',
    'error.min_value': 'Valoarea minimă este {min}',
    'error.max_value': 'Valoarea maximă este {max}',
    'error.upload_failed': 'Încărcarea imaginii a eșuat',
    'error.network_error': 'Eroare de rețea. Verificați conexiunea.',
    'error.server_error': 'Eroare de server. Încercați din nou mai târziu.',
    
    // Confirmation messages
    'confirm.reset_form': 'Sigur doriți să resetați formularul?',
    'confirm.clear_data': 'Toate datele vor fi șterse',
    'confirm.delete_image': 'Sigur doriți să ștergeți această imagine?',
    'confirm.leave_page': 'Aveți modificări nesalvate. Sigur doriți să părăsiți pagina?',
    
    // Success messages
    'success.listing_saved': 'Anunț salvat cu succes!',
    'success.image_uploaded': 'Imagine încărcată cu succes',
    'success.form_reset': 'Formularul a fost resetat',
    
    // Info messages
    'info.analyzing': 'Se analizează imaginile...',
    'info.uploading': 'Se încarcă...',
    'info.saving': 'Se salvează anunțul...',
    'info.loading': 'Se încarcă...',
  }
};

// Helper for parameterized messages
export function t(key: string, params?: Record<string, any>): string {
  let message = translations.ro[key] || key;
  
  if (params) {
    Object.keys(params).forEach(param => {
      message = message.replace(`{${param}}`, params[param]);
    });
  }
  
  return message;
}
```

### 5. Backend Error Messages

**File:** `backend/app/main.py`

**Update API error responses:**

```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return Romanian error messages."""
    
    error_messages = {
        400: "Cerere invalidă",
        404: "Resursa nu a fost găsită",
        500: "Eroare internă de server",
    }
    
    detail = error_messages.get(exc.status_code, exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail}
    )

# Validation errors
@app.post("/api/listings")
async def create_listing(listing: ListingCreate):
    if not listing.property_type:
        raise HTTPException(
            status_code=400,
            detail="Tipul proprietății este obligatoriu"
        )
    
    if not listing.images:
        raise HTTPException(
            status_code=400,
            detail="Este necesară cel puțin o imagine"
        )
    
    # ... rest of endpoint
```

## Acceptance Criteria

- [ ] All error messages in Romanian
- [ ] All validation messages in Romanian
- [ ] All confirmation dialogs in Romanian
- [ ] Success messages in Romanian
- [ ] Info/loading messages in Romanian
- [ ] Backend API errors in Romanian
- [ ] Parameterized messages work (e.g., "Field {name} is required")
- [ ] Messages are grammatically correct
- [ ] Messages are user-friendly (not technical jargon)

## Testing Checklist

### Frontend Errors
- [ ] Try to preview without property type → see Romanian error
- [ ] Try to save without images → see Romanian error
- [ ] Enter invalid number in price field → see Romanian error
- [ ] Click reset button → see Romanian confirmation

### Backend Errors
- [ ] Send invalid request → see Romanian error
- [ ] Send request without required field → see Romanian error
- [ ] Simulate server error → see Romanian error message

### Success Messages
- [ ] Save listing → see Romanian success message
- [ ] Upload image → see Romanian success message
- [ ] Reset form → see Romanian confirmation

## Notes

- Use natural, conversational Romanian
- Avoid technical terms where possible
- Error messages should be helpful, not just state the problem
- Include guidance on how to fix the error when possible
- Get native speaker review for tone and clarity
