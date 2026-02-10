# TASK-042: Add Romanian Room and Amenity Translations

**Story:** STORY-008 (Romanian Localization)
**Status:** todo
**Priority:** medium
**Assigned:** -
**Effort:** 2 hours
**Depends on:** TASK-037

## Objective

Complete translation coverage for all room types and amenities detected by the vision model.

## Files to Update

### 1. Expand i18n Translations

**File:** `frontend/src/lib/i18n/index.ts`

**Add comprehensive room types:**

```typescript
export const translations = {
  ro: {
    // ... existing translations ...
    
    // Room types (complete list)
    'room.bedroom': 'Dormitor',
    'room.kitchen': 'Bucătărie',
    'room.living_room': 'Sufragerie',
    'room.dining_room': 'Cameră de Mâncare',
    'room.bathroom': 'Baie',
    'room.hallway': 'Hol',
    'room.office': 'Birou',
    'room.balcony': 'Balcon',
    'room.garage': 'Garaj',
    'room.laundry_room': 'Cameră de Spălătorie',
    'room.closet': 'Dressing',
    'room.pantry': 'Cămară',
    'room.basement': 'Subsol',
    'room.attic': 'Mansardă',
    'room.mudroom': 'Cameră de Haine',
    'room.study': 'Birou de Studiu',
    'room.library': 'Bibliotecă',
    'room.gym': 'Sală de Sport',
    'room.media_room': 'Cameră Media',
    'room.game_room': 'Cameră de Jocuri',
    'room.wine_cellar': 'Pivniță de Vin',
    'room.sunroom': 'Cameră cu Soare',
    'room.conservatory': 'Seră',
    'room.porch': 'Verandă',
    'room.patio': 'Patio',
    'room.deck': 'Terasă',
    'room.staircase': 'Scară',
    'room.open_concept_space': 'Spațiu Open-Concept',
    
    // Amenities (complete list)
    'amenity.hardwood_floors': 'Parchet',
    'amenity.tile_floors': 'Pardoseală cu Gresie',
    'amenity.carpet': 'Mochetă',
    'amenity.granite_counters': 'Blat de Granit',
    'amenity.marble_counters': 'Blat de Marmură',
    'amenity.quartz_counters': 'Blat de Cuarț',
    'amenity.stainless_steel': 'Oțel Inoxidabil',
    'amenity.stainless_steel_appliances': 'Aparate din Oțel Inoxidabil',
    'amenity.fireplace': 'Șemineu',
    'amenity.dishwasher': 'Mașină de Spălat Vase',
    'amenity.microwave': 'Cuptor cu Microunde',
    'amenity.oven': 'Cuptor',
    'amenity.refrigerator': 'Frigider',
    'amenity.washer': 'Mașină de Spălat',
    'amenity.dryer': 'Uscător',
    'amenity.pool': 'Piscină',
    'amenity.hot_tub': 'Cadă cu Hidromasaj',
    'amenity.sauna': 'Saună',
    'amenity.garage': 'Garaj',
    'amenity.parking': 'Parcare',
    'amenity.garden': 'Grădină',
    'amenity.yard': 'Curte',
    'amenity.fence': 'Gard',
    'amenity.gate': 'Poartă',
    'amenity.security_system': 'Sistem de Securitate',
    'amenity.alarm': 'Alarmă',
    'amenity.intercom': 'Interfon',
    'amenity.elevator': 'Lift',
    'amenity.air_conditioning': 'Aer Condiționat',
    'amenity.central_heating': 'Încălzire Centrală',
    'amenity.ceiling_fan': 'Ventilator de Tavan',
    'amenity.skylight': 'Fereastră de Mansardă',
    'amenity.bay_window': 'Fereastră Bow',
    'amenity.french_doors': 'Uși Franceze',
    'amenity.sliding_doors': 'Uși Glisante',
    'amenity.walk_in_closet': 'Dressing',
    'amenity.built_in_shelves': 'Rafturi Încorporate',
    'amenity.crown_molding': 'Cornișă',
    'amenity.recessed_lighting': 'Iluminare Încastrată',
    'amenity.pendant_lights': 'Lustre Suspendate',
    'amenity.chandelier': 'Candelabru',
    
    // Materials
    'material.wood': 'Lemn',
    'material.hardwood': 'Lemn Masiv',
    'material.tile': 'Gresie',
    'material.marble': 'Marmură',
    'material.granite': 'Granit',
    'material.quartz': 'Cuarț',
    'material.concrete': 'Beton',
    'material.brick': 'Cărămidă',
    'material.stone': 'Piatră',
    'material.glass': 'Sticlă',
    'material.metal': 'Metal',
    'material.stainless_steel': 'Oțel Inoxidabil',
    
    // Styles
    'style.modern': 'Modern',
    'style.contemporary': 'Contemporan',
    'style.traditional': 'Tradițional',
    'style.rustic': 'Rustic',
    'style.industrial': 'Industrial',
    'style.minimalist': 'Minimalist',
    'style.scandinavian': 'Scandinav',
    'style.mediterranean': 'Mediteranean',
    'style.colonial': 'Colonial',
    'style.victorian': 'Victorian',
    'style.farmhouse': 'Fermă',
    'style.cottage': 'Cabană',
    'style.craftsman': 'Meșteșugăresc',
    'style.mid_century': 'Mijloc de Secol',
  }
};
```

### 2. Update SynthesisDisplay Component

**File:** `frontend/src/lib/components/SynthesisDisplay.svelte`

**Update room and amenity display:**

```svelte
<script>
  import { getRoomLabel, getAmenityLabel } from '$lib/i18n';
  
  function formatRoomName(roomType: string): string {
    return getRoomLabel(roomType);
  }
  
  function formatAmenity(amenity: string): string {
    return getAmenityLabel(amenity);
  }
</script>

<!-- Display rooms with Romanian labels -->
{#each Object.entries(synthesis.room_breakdown) as [roomType, count]}
  <div class="room-item">
    <span class="room-icon">{getRoomIcon(roomType)}</span>
    <span class="room-name">{formatRoomName(roomType)}</span>
  </div>
{/each}

<!-- Display amenities with Romanian labels -->
{#each amenities as amenity}
  <span class="amenity-tag">
    {formatAmenity(amenity)}
  </span>
{/each}
```

### 3. Update Backend Vision Model

**File:** `backend/app/vision_model.py`

**Ensure all room types and amenities are translated:**

```python
def _translate_room_type(room_type: str) -> str:
    """Translate room type to Romanian."""
    translations = {
        'bedroom': 'Dormitor',
        'kitchen': 'Bucătărie',
        'living_room': 'Sufragerie',
        'dining_room': 'Cameră de Mâncare',
        'bathroom': 'Baie',
        'hallway': 'Hol',
        'office': 'Birou',
        'balcony': 'Balcon',
        'garage': 'Garaj',
        'laundry_room': 'Cameră de Spălătorie',
        'closet': 'Dressing',
        'pantry': 'Cămară',
        'basement': 'Subsol',
        'attic': 'Mansardă',
        'study': 'Birou de Studiu',
        'gym': 'Sală de Sport',
        'media_room': 'Cameră Media',
        'game_room': 'Cameră de Jocuri',
        'porch': 'Verandă',
        'patio': 'Patio',
        'deck': 'Terasă',
        'staircase': 'Scară',
        'open_concept_space': 'Spațiu Open-Concept',
    }
    return translations.get(room_type, room_type.replace('_', ' ').title())

def _translate_amenity(amenity: str) -> str:
    """Translate amenity to Romanian."""
    translations = {
        'hardwood_floors': 'parchet',
        'granite_counters': 'blat de granit',
        'marble_counters': 'blat de marmură',
        'stainless_steel_appliances': 'aparate din oțel inoxidabil',
        'fireplace': 'șemineu',
        'dishwasher': 'mașină de spălat vase',
        'pool': 'piscină',
        'hot_tub': 'cadă cu hidromasaj',
        'garage': 'garaj',
        'garden': 'grădină',
        'air_conditioning': 'aer condiționat',
        'central_heating': 'încălzire centrală',
        'walk_in_closet': 'dressing',
    }
    return translations.get(amenity, amenity.replace('_', ' '))
```

## Acceptance Criteria

- [ ] All room types have Romanian translations
- [ ] All amenities have Romanian translations
- [ ] All materials have Romanian translations
- [ ] All styles have Romanian translations
- [ ] SynthesisDisplay shows Romanian room names
- [ ] SynthesisDisplay shows Romanian amenity names
- [ ] Backend generates descriptions with Romanian terms
- [ ] No untranslated terms visible to user
- [ ] Fallback to English if translation missing

## Testing

### Manual Test

1. Upload images with various rooms:
   - Bedroom → "Dormitor"
   - Kitchen → "Bucătărie"
   - Living Room → "Sufragerie"

2. Check amenities display:
   - Hardwood Floors → "Parchet"
   - Granite Counters → "Blat de Granit"
   - Fireplace → "Șemineu"

3. Check property description:
   - "Acest apartament include Dormitor, Bucătărie..."
   - "Caracteristici includ parchet, șemineu..."

### Automated Test

```typescript
test('displays room types in Romanian', async () => {
  // Mock synthesis data with bedroom
  const synthesis = {
    room_breakdown: {
      'bedroom': 1,
      'kitchen': 1
    }
  };
  
  const { getByText } = render(SynthesisDisplay, { synthesis });
  
  expect(getByText('Dormitor')).toBeInTheDocument();
  expect(getByText('Bucătărie')).toBeInTheDocument();
});
```

## Notes

- Translations should be lowercase in descriptions, title case in UI labels
- Use proper Romanian diacritics (ă, â, î, ș, ț)
- Some English terms are commonly used in Romanian real estate (e.g., "open-concept")
- Verify translations with native speaker
- Consider regional variations (e.g., "sufragerie" vs "living")
