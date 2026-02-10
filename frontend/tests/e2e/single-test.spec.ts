import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test('single working test', async ({ page }) => {
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  
  // Verify landing page
  await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
  
  // Upload image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
  
  // Wait for analysis
  await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
  
  // Fill form
  await page.locator('select[id="property_type"]').selectOption('apartment');
  await page.fill('input[id="price"]', '350000');
  await page.fill('input[id="bedrooms"]', '2');
  await page.fill('input[id="bathrooms"]', '1');
  
  // Progress to completion
  let completion = 0;
  let attempts = 0;
  while (completion < 100 && attempts < 20) {
    const completionText = await page.locator('.progress-text').textContent();
    completion = parseInt(completionText?.replace('% Complete', '') || '0');
    
    if (completion >= 100) break;
    
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(1000);
    attempts++;
  }
  
  // Verify completion
  await expect(page.locator('text=100% Complete')).toBeVisible();
  
  // Go to preview
  await page.click('button:has-text("Preview Listing")');
  await expect(page.locator('text=Your Listing Preview')).toBeVisible();
  
  // Success
  expect(true).toBeTruthy();
});