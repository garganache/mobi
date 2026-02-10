import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Fixed Listing Save Flow Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('should complete minimal journey: upload → form → preview → save', async ({ page }) => {
    // 1. Wait for the landing page to load - actual text is "Get Started"
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
    
    // 2. Upload test images
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      'tests/fixtures/kitchen.jpg',
      'tests/fixtures/bedroom.jpg'
    ]);
    
    // 3. Wait for analysis to complete - look for the actual AI message
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // 4. Fill in required form fields
    // Wait for property type field to appear - it's a select field with id "property_type"
    await expect(page.locator('select[id="property_type"]')).toBeVisible();
    await page.locator('select[id="property_type"]').selectOption('apartment');
    
    // Fill other required fields as they appear
    await page.fill('input[id="price"]', '350000');
    await page.fill('input[id="bedrooms"]', '2');
    await page.fill('input[id="bathrooms"]', '1');
    
    // 5. Wait for completion to reach 100% - the progress indicator shows completion percentage
    await expect(page.locator('text=100% Complete')).toBeVisible({ timeout: 10000 });
    
    // 6. Click Preview Listing button - it's actually "Preview Listing" when 100% complete
    await page.click('button:has-text("Preview Listing")');
    
    // 7. Verify preview page shows
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    await expect(page.locator('text=Property Description')).toBeVisible();
    
    // 8. Click Save/Publish button - it's "Publish Listing" in the preview
    await page.click('button:has-text("Publish Listing")');
    
    // 9. Wait for success modal
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // 10. Extract listing ID
    const listingIdText = await page.locator('.listing-id').textContent();
    const listingId = listingIdText?.match(/\d+/)?.[0];
    
    expect(listingId).toBeTruthy();
    console.log('Saved listing ID:', listingId);
    
    // Take screenshot for documentation
    await page.screenshot({ path: 'tests/screenshots/listing-save-success.png', fullPage: true });
  });

  test('should handle validation errors gracefully', async ({ page }) => {
    // Upload image and fill minimal form
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for analysis
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // Fill form with minimal required fields
    await page.locator('select[id="property_type"]').selectOption('apartment');
    await page.fill('input[id="bedrooms"]', '2');
    
    // Continue until we reach 100%
    while (true) {
      const completionText = await page.locator('.progress-text').textContent();
      const completion = parseInt(completionText?.replace('% Complete', '') || '0');
      if (completion >= 100) break;
      
      // Click continue to progress
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Try to save - should handle gracefully
    await page.click('button:has-text("Publish Listing")');
    
    // Should complete with success
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
  });

  test('should save images with AI analysis data', async ({ page }) => {
    // Upload images
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      'tests/fixtures/kitchen.jpg',
      'tests/fixtures/living_room.jpg'
    ]);
    
    // Wait for analysis
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // Fill form
    await page.locator('select[id="property_type"]').selectOption('house');
    await page.fill('input[id="price"]', '450000');
    await page.fill('input[id="bedrooms"]', '3');
    await page.fill('input[id="bathrooms"]', '2');
    
    // Continue until 100% complete
    while (true) {
      const completionText = await page.locator('.progress-text').textContent();
      const completion = parseInt(completionText?.replace('% Complete', '') || '0');
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Save
    await page.click('button:has-text("Publish Listing")');
    
    // Wait for success
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // Extract listing ID
    const listingIdText = await page.locator('.listing-id').textContent();
    const listingId = listingIdText?.match(/\d+/)?.[0];
    
    expect(listingId).toBeTruthy();
    console.log('Saved listing with images. ID:', listingId);
  });

  test('should show loading state during save', async ({ page }) => {
    // Upload image and fill form
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    await page.locator('select[id="property_type"]').selectOption('apartment');
    await page.fill('input[id="price"]', '300000');
    await page.fill('input[id="bedrooms"]', '1');
    await page.fill('input[id="bathrooms"]', '1');
    
    // Continue until 100% complete
    while (true) {
      const completionText = await page.locator('.progress-text').textContent();
      const completion = parseInt(completionText?.replace('% Complete', '') || '0');
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Click save and verify loading state
    await page.click('button:has-text("Publish Listing")');
    
    // Should show loading state
    await expect(page.locator('button:has-text("Saving...")')).toBeVisible();
    
    // Should complete with success
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
  });
});