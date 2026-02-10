# TASK-037: Create i18n Infrastructure

**Story:** STORY-008 (Romanian Localization)
**Status:** done
**Priority:** high
**Assigned:** -
**Effort:** 3 hours

## Objective

Create the translation infrastructure and Romanian translation files for the frontend.

## Requirements

### Create Translation System

**File:** `frontend/src/lib/i18n/index.ts`

```typescript
export const translations = {
  ro: {
    // Property types
    'property_type.apartment': 'Apartament',
    'property_type.house': 'Casă',
    'property_type.condo': 'Condominium',
    'property_type.townhouse': 'Casă în Șir',
    'property_type.land': 'Teren',
    'property_type.commercial': 'Comercial',
    
    // Fields
    'field.property_type': 'Tipul Proprietății',
    'field.price': 'Preț',
    'field.bedrooms': 'Dormitoare',
    'field.bathrooms': 'Băi',
    'field.square_feet': 'Suprafață (metri pătrați)',
    'field.address': 'Adresă',
    'field.city': 'Oraș',
    'field.state': 'Județ',
    'field.zip': 'Cod Poștal',
    'field.description': 'Descriere',
    
    // Rooms
    'room.bedroom': 'Dormitor',
    'room.kitchen': 'Bucătărie',
    'room.living_room': 'Sufragerie',
    'room.bathroom': 'Baie',
    'room.hallway': 'Hol',
    'room.dining_room': 'Cameră de Mâncare',
    'room.office': 'Birou',
    'room.balcony': 'Balcon',
    
    // Amenities
    'amenity.hardwood_floors': 'Parchet',
    'amenity.granite_counters': 'Blat de Granit',
    'amenity.fireplace': 'Șemineu',
    'amenity.dishwasher': 'Mașină de Spălat Vase',
    'amenity.pool': 'Piscină',
    'amenity.garage': 'Garaj',
    'amenity.garden': 'Grădină',
    
    // Buttons
    'button.continue': 'Continuă',
    'button.preview': 'Previzualizare Anunț',
    'button.save': 'Salvează Anunțul',
    'button.preview_save': 'Previzualizare și Salvare',
    'button.reset': 'Resetează formularul',
    'button.start': 'Începe',
    'button.upload': 'Încarcă',
    'button.edit': 'Editează',
    'button.create_another': 'Creează Alt Anunț',
    'button.view_listing': 'Vezi Anunț',
    
    // Messages
    'message.drop_photo': 'Pune o poză pentru a începe anunțul',
    'message.images_analyzed': 'imagini analizate',
    'message.rooms_detected': 'Camere detectate în imagini',
    'message.listing_complete': 'Anunț Complet!',
    'message.listing_saved': 'Anunț salvat cu succes',
    'message.check_details': 'Verificați toate detaliile anunțului dvs',
    
    // Headers
    'header.property_overview': 'Prezentare Proprietate',
    'header.preview_listing': 'Previzualizare Anunț',
    
    // Errors
    'error.property_type_required': 'Selectați tipul proprietății înainte de previzualizare',
    'error.images_required': 'Este necesară cel puțin o imagine',
    'error.invalid_price': 'Prețul trebuie să fie un număr valid',
    'error.save_failed': 'Nu s-a putut salva anunțul',
    
    // Confirmations
    'confirm.reset_form': 'Sigur doriți să resetați formularul?',
    'confirm.clear_data': 'Toate datele vor fi șterse',
  }
};

export function t(key: string, locale: string = 'ro'): string {
  return translations[locale]?.[key] || key;
}

// Helper for property type labels
export function getPropertyTypeLabel(value: string): string {
  return t(`property_type.${value}`);
}

// Helper for room labels
export function getRoomLabel(value: string): string {
  return t(`room.${value}`);
}

// Helper for amenity labels
export function getAmenityLabel(value: string): string {
  return t(`amenity.${value}`);
}
```

### Create Type Definitions

**File:** `frontend/src/lib/i18n/types.ts`

```typescript
export type Locale = 'ro' | 'en';

export interface TranslationKey {
  key: string;
  defaultValue?: string;
}

export interface I18nConfig {
  defaultLocale: Locale;
  supportedLocales: Locale[];
}
```

## Acceptance Criteria

- [x] Translation file created with all Romanian strings
- [x] Translation function `t()` works correctly
- [x] Helper functions for property types, rooms, amenities
- [x] Type definitions created
- [x] No TypeScript errors
- [x] Can import and use in components

## Testing

```typescript
import { t, getPropertyTypeLabel, getRoomLabel } from '$lib/i18n';

console.log(t('button.continue')); // "Continuă"
console.log(getPropertyTypeLabel('apartment')); // "Apartament"
console.log(getRoomLabel('bedroom')); // "Dormitor"
```

## Notes

- Keep translation keys in English for code clarity
- Use dot notation for namespacing (e.g., `button.continue`)
- Add more translations as needed during implementation
- Structure allows easy addition of more languages later
