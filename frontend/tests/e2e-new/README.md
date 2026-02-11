# New E2E Test Suite

**Status:** ✅ Production-ready (100% passing)

This test suite is specifically designed for the Romanian production deployment at `http://151.115.14.38`.

## Quick Start

```bash
# Run all tests
E2E_BASE_URL=http://151.115.14.38 npx playwright test --config=playwright-new.config.ts

# Run with UI (debug mode)
E2E_BASE_URL=http://151.115.14.38 npx playwright test --config=playwright-new.config.ts --ui

# Run specific category
E2E_BASE_URL=http://151.115.14.38 npx playwright test tests/e2e-new/01-basic-ui.spec.ts --config=playwright-new.config.ts
```

## Test Files

1. **01-basic-ui.spec.ts** - Basic UI and Romanian interface
2. **02-image-upload.spec.ts** - Image upload functionality
3. **03-form-interaction.spec.ts** - Form field interactions
4. **04-romanian-localization.spec.ts** - Romanian text verification
5. **05-complete-flow.spec.ts** - End-to-end user journeys

## Helpers

`helpers.ts` provides reusable utilities:
- `uploadImage()` - Upload single image with proper timing
- `uploadMultipleImages()` - Upload multiple images
- `verifyUploadedImages()` - Confirm upload success
- `fillPropertyForm()` - Fill form fields
- `clickContinue()` - Click Continue button
- `waitForFormField()` - Wait for form fields to appear
- `RO` constant - Romanian text constants

## Design Principles

### 1. Production-First
- Tests run against actual production deployment
- No localhost assumptions
- Realistic timeouts (production is slower)

### 2. Romanian-Native
- All text expectations in Romanian
- No English hardcoding
- Flexible text matching for AI responses

### 3. Resilient Selectors
- Multiple selector fallbacks
- Checks for actual behavior, not implementation
- Handles progressive form reveal

### 4. Fast & Focused
- 21 tests covering core functionality
- ~1 minute runtime
- No redundant checks

## Production Specifics

### Form Fields (After Continue)
```javascript
{
  bedrooms: 'input#bedrooms',        // Număr de Dormitoare
  bathrooms: 'input#bathrooms',      // Număr de Băi
  squareFeet: 'input#square_feet'    // Suprafață (metri pătrați)
}
```

**Note:** No `price` field exists in production.

### Upload Verification
Instead of `.upload-item`, check for:
- `h3:has-text("Prezentare Proprietate")`
- `text=/\\d+ imagin/i` (e.g., "1 imagine analizată")

### AI Messages
Production AI responses vary:
- "Nu au fost detectate camere în imaginile furnizate."
- "Să începem prin a identifica ce tip de proprietate..."
- "Excelent! Am identificat că este vorba despre un casă..."

Tests check for Romanian patterns, not exact strings.

## Extending Tests

To add new tests:

```typescript
import { test, expect } from '@playwright/test';
import { BASE_URL, RO, FIXTURES, uploadImage } from './helpers';

test.describe('My New Feature', () => {
  test('should do something', async ({ page }) => {
    await page.goto(BASE_URL);
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Your test logic here
    await expect(page.locator('...')).toBeVisible();
  });
});
```

## Troubleshooting

### Tests timing out?
- Increase `timeout` in `playwright-new.config.ts`
- Production can be slow during peak hours

### Selectors not found?
- Check production DOM with inspect tests:
  ```bash
  E2E_BASE_URL=http://151.115.14.38 npx playwright test tests/e2e-new/inspect-actual-dom.spec.ts --config=playwright-new.config.ts
  ```

### AI message assertions failing?
- AI responses vary based on image analysis
- Use flexible pattern matching, not exact strings

## Migration from Old Tests

If you need functionality from the old test suite (`tests/e2e/`):

1. Check if it's already covered in the new suite
2. If not, extract the core assertion
3. Rewrite using production-specific selectors
4. Test against actual production behavior

**Don't port blindly** - the old tests had many incorrect assumptions.
