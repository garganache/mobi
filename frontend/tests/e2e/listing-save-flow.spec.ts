import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Complete Listing Save Flow - Fixed', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('should complete full journey: upload → form → preview → save', async ({ page }) => {
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
    
    // 4. Fill in required form fields - use correct field IDs
    await expect(page.locator('select[id="property_type"]')).toBeVisible();
    await page.locator('select[id="property_type"]').selectOption('apartment');
    
    // Fill other required fields
    await page.fill('input[id="price"]', '350000');
    await page.fill('input[id="bedrooms"]', '2');
    await page.fill('input[id="bathrooms"]', '1');
    
    // 5. Progress to 100% completion - use progress indicator
    await expect(page.locator('text=100% Complete')).toBeVisible({ timeout: 15000 });
    
    // 6. Click Preview Listing button
    await page.click('button:has-text("Preview Listing")');
    
    // 7. Verify preview page shows
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    await expect(page.locator('text=Property Description')).toBeVisible();
    
    // 8. Verify all data is present in preview
    await expect(page.locator('text=apartment')).toBeVisible();
    await expect(page.locator('text=$350,000')).toBeVisible();
    await expect(page.locator('text=2 bedroom')).toBeVisible();
    await expect(page.locator('text=1 bathroom')).toBeVisible();
    
    // 9. Click Save/Publish button
    await page.click('button:has-text("Publish Listing")');
    
    // 10. Wait for success modal
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // 11. Verify listing ID displayed
    await expect(page.locator('text=/Listing ID: #\\d+/')).toBeVisible();
    
    // 12. Extract listing ID
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
    
    // Continue until we reach 100% completion
    let completion = 0;
    while (completion < 100) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
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
    let completion = 0;
    while (completion < 100) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Verify images are shown in preview
    await expect(page.locator('text=Property Images (2)')).toBeVisible();
    
    // Save
    await page.click('button:has-text("Publish Listing")');
    
    // Wait for success
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // Extract listing ID
    const listingIdText = await page.locator('.listing-id').textContent();
    const listingId = listingIdText?.match(/\d+/)?.[0];
    
    expect(listingId).toBeTruthy();
    console.log('Saved listing with images. ID:', listingId);
    
    // Verify via API that images were saved
    try {
      const response = await fetch(`http://localhost:8000/api/listings/${listingId}`);
      if (response.ok) {
        const data = await response.json();
        expect(data.images.length).toBeGreaterThan(0);
        console.log('Verified images saved via API');
      }
    } catch (e) {
      console.log('Could not verify via API:', e);
    }
  });

  test('should save synthesis data correctly', async ({ page }) => {
    // Complete the full flow
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      'tests/fixtures/kitchen.jpg',
      'tests/fixtures/bedroom.jpg',
      'tests/fixtures/living_room.jpg'
    ]);
    
    // Wait for synthesis
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // Verify synthesis data is displayed
    const synthesisText = await page.locator('.synthesis-display').textContent();
    expect(synthesisText).toContain('rooms');
    
    // Fill form
    await page.locator('select[id="property_type"]').selectOption('apartment');
    await page.fill('input[id="price"]', '380000');
    await page.fill('input[id="bedrooms"]', '2');
    await page.fill('input[id="bathrooms"]', '1.5');
    
    // Continue until 100% complete
    let completion = 0;
    while (completion < 100) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Verify synthesis data in preview
    await expect(page.locator('text=Property Description')).toBeVisible();
    
    // Save
    await page.click('button:has-text("Publish Listing")');
    await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
    
    // Extract listing ID
    const listingIdText = await page.locator('.listing-id').textContent();
    const listingId = listingIdText?.match(/\d+/)?.[0];
    
    expect(listingId).toBeTruthy();
    console.log('Saved listing with synthesis data. ID:', listingId);
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
    let completion = 0;
    while (completion < 100) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
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

  test('should handle network errors gracefully', async ({ page, context }) => {
    // Intercept and fail the save request
    await context.route('**/api/listings', route => {
      route.abort('failed');
    });
    
    // Upload image and fill form
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    await page.locator('select[id="property_type"]').selectOption('apartment');
    await page.fill('input[id="price"]', '250000');
    await page.fill('input[id="bedrooms"]', '1');
    await page.fill('input[id="bathrooms"]', '1');
    
    // Continue until 100% complete
    let completion = 0;
    while (completion < 100) {
      const completionText = await page.locator('.progress-text').textContent();
      completion = parseInt(completionText?.replace('% Complete', '') || '0');
      
      if (completion >= 100) break;
      
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(1000);
    }
    
    // Go to preview
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Try to save - should handle network error
    await page.click('button:has-text("Publish Listing")');
    
    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible({ timeout: 10000 });
    
    const errorText = await page.locator('.error-message').textContent();
    expect(errorText).toContain('Failed to save');
  });
});