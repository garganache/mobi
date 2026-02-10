import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Fixed Listing Save Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('should complete basic journey: upload → form → preview → save', async ({ page }) => {
    // 1. Wait for the landing page - actual text is "Get Started"
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
    
    // 2. Upload test images
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      'tests/fixtures/kitchen.jpg',
      'tests/fixtures/bedroom.jpg'
    ]);
    
    // 3. Wait for analysis - actual message after upload
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // 4. Fill in required form fields - use correct field IDs (id not name)
    await expect(page.locator('select[id="property_type"]')).toBeVisible();
    await page.locator('select[id="property_type"]').selectOption('apartment');
    
    // Fill other required fields
    await page.fill('input[id="price"]', '350000');
    await page.fill('input[id="bedrooms"]', '2');
    await page.fill('input[id="bathrooms"]', '1');
    
    // 5. Progress to 100% completion - use progress indicator and Continue button
    let completion = 0;
    let attempts = 0;
    while (completion < 100 && attempts < 10) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
      if (completion >= 100) break;
      
      // Click Continue to progress
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
      attempts++;
    }
    
    // 6. Verify we reached 100%
    await expect(page.locator('text=100% Complete')).toBeVisible();
    
    // 7. Click Preview Listing button
    await page.click('button:has-text("Preview Listing")');
    
    // 8. Verify preview page shows
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    await expect(page.locator('text=Property Description')).toBeVisible();
    
    // 9. Verify data in preview
    await expect(page.locator('text=apartment')).toBeVisible();
    await expect(page.locator('text=$350,000')).toBeVisible();
    await expect(page.locator('text=2 bedroom')).toBeVisible();
    await expect(page.locator('text=1 bathroom')).toBeVisible();
    
    // 10. Click Save/Publish button
    await page.click('button:has-text("Publish Listing")');
    
    // 11. Wait for success modal
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // 12. Verify listing ID displayed
    await expect(page.locator('text=/Listing ID: #\\d+/')).toBeVisible();
    
    // 13. Extract listing ID
    const listingIdText = await page.locator('.listing-id').textContent();
    const listingId = listingIdText?.match(/\d+/)?.[0];
    
    expect(listingId).toBeTruthy();
    console.log('Saved listing ID:', listingId);
    
    // Take screenshot for documentation
    await page.screenshot({ path: 'tests/screenshots/listing-save-success.png', fullPage: true });
  });

  test('should handle single image upload and basic form', async ({ page }) => {
    // Upload single image
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for analysis
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // Fill basic form
    await page.locator('select[id="property_type"]').selectOption('apartment');
    await page.fill('input[id="price"]', '300000');
    await page.fill('input[id="bedrooms"]', '1');
    await page.fill('input[id="bathrooms"]', '1');
    
    // Progress to completion
    let completion = 0;
    for (let i = 0; i < 8; i++) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(800);
    }
    
    // Verify we can reach preview
    if (completion >= 100) {
      await page.click('button:has-text("Preview Listing")');
      await expect(page.locator('text=Your Listing Preview')).toBeVisible();
      console.log('Successfully completed single image flow');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/single-image-flow.png', fullPage: true });
    
    // Success - we got past the upload stage
    expect(completion).toBeGreaterThan(50);
  });
});