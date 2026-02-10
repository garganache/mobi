import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Simple Working Flow Test', () => {
  test('basic upload and form progression', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Verify we're on the right page
    await expect(page.locator('h1:has-text("Mobi Property Listing")')).toBeVisible();
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
    
    // Upload a single image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for the AI message to change from the default
    await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
    
    // Fill the property type field
    await page.locator('select[id="property_type"]').selectOption('apartment');
    
    // Fill price
    await page.fill('input[id="price"]', '350000');
    
    // Fill bedrooms
    await page.fill('input[id="bedrooms"]', '2');
    
    // Fill bathrooms
    await page.fill('input[id="bathrooms"]', '1');
    
    // Take screenshot to document the state
    await page.screenshot({ path: 'test-results/basic-form-filled.png', fullPage: true });
    
    // Click continue until we reach 100%
    let attempts = 0;
    while (attempts < 10) {
      const completionText = await page.locator('.progress-text').textContent();
      const completion = parseInt(completionText?.replace('% Complete', '') || '0');
      console.log(`Current completion: ${completion}%`);
      
      if (completion >= 100) {
        break;
      }
      
      // Click continue
      await page.click('button:has-text("Continue")');
      await page.waitForTimeout(2000);
      attempts++;
    }
    
    // Verify we reached 100%
    await expect(page.locator('text=100% Complete')).toBeVisible();
    
    // Click Preview Listing
    await page.click('button:has-text("Preview Listing")');
    
    // Verify we're in preview mode
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/basic-preview.png', fullPage: true });
    
    // Success - basic flow works
    expect(true).toBeTruthy();
  });
});