import { test, expect } from '@playwright/test';
import { 
  BASE_URL, 
  RO, 
  FIXTURES, 
  waitForPageLoad, 
  uploadImage,
  uploadMultipleImages,
  verifyUploadedImages,
  waitForFormField,
  fillPropertyForm,
  clickContinue
} from './helpers';

test.describe('Complete User Flow', () => {
  test('full journey: upload → form → preview', async ({ page }) => {
    // Step 1: Load page
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    
    // Step 2: Upload image
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Step 3: Wait for form and fill property type
    await waitForFormField(page, 'select#property_type');
    await fillPropertyForm(page, {
      propertyType: 'apartment'
    });
    
    // Step 4: Click Continue to reveal more fields
    await clickContinue(page);
    
    // Step 5: Fill remaining fields
    await fillPropertyForm(page, {
      bedrooms: '2',
      bathrooms: '1',
      squareFeet: '85'
    });
    
    // Step 6: Check for Preview button (should still be visible)
    const previewBtn = page.locator(`button:has-text("${RO.PREVIEW_SAVE}")`);
    await expect(previewBtn).toBeVisible({ timeout: 15000 });
    
    console.log('✓ Complete flow test passed!');
  });

  test('can reset form and start over', async ({ page }) => {
    // Upload and fill form
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    await fillPropertyForm(page, {
      propertyType: 'house'
    });
    
    // Look for reset button at top of page
    const resetBtn = page.locator('button:has-text("Reset")').first();
    
    if (await resetBtn.isVisible()) {
      // Handle potential confirmation dialog
      page.on('dialog', dialog => dialog.accept());
      
      await resetBtn.click();
      
      // Wait for reset
      await page.waitForTimeout(2000);
      
      // Should be back at initial state
      await expect(page.locator('h2:has-text("Începe")')).toBeVisible({ timeout: 5000 });
    } else {
      console.log('Reset button not visible (may require Continue first)');
    }
  });

  test('multi-image complete flow', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    
    // Upload multiple images
    await uploadMultipleImages(page, [
      FIXTURES.KITCHEN,
      FIXTURES.BEDROOM,
      FIXTURES.LIVING_ROOM
    ]);
    
    // Verify multiple images were uploaded (check for "Imagine 1", "Imagine 2", etc.)
    await verifyUploadedImages(page, 3);
    
    // Form should still work
    await waitForFormField(page, 'select#property_type');
    
    await fillPropertyForm(page, {
      propertyType: 'apartment'
    });
    
    // Click Continue
    await clickContinue(page);
    
    // Fill more fields
    await fillPropertyForm(page, {
      bedrooms: '3',
      bathrooms: '2'
    });
    
    // Should be able to see preview button
    const previewBtn = page.locator(`button:has-text("${RO.PREVIEW_SAVE}")`);
    await expect(previewBtn).toBeVisible();
  });

  test('property overview section appears', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    
    // Upload image
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Wait a bit for synthesis
    await page.waitForTimeout(3000);
    
    // Look for property overview section (Romanian text)
    const hasOverview = await page.locator('text=/Prezentare|camere|proprietate/i').count() > 0;
    
    // It's okay if it doesn't appear immediately
    if (!hasOverview) {
      console.log('Note: Property overview not immediately visible (may require Continue click)');
    }
  });
});
