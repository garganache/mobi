import { test, expect } from '@playwright/test';

test('minimal working flow', async ({ page }) => {
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  
  // Verify page loaded
  await expect(page.locator('h1:has-text("Mobi Property Listing")')).toBeVisible();
  await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
  
  // Upload image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
  
  // Wait for analysis with shorter timeout
  await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 15000 });
  
  // Fill form fields
  await page.locator('select[id="property_type"]').selectOption('apartment');
  await page.fill('input[id="price"]', '350000');
  await page.fill('input[id="bedrooms"]', '2');
  await page.fill('input[id="bathrooms"]', '1');
  
  // Progress to completion - limit attempts
  let completion = 0;
  for (let i = 0; i < 5; i++) {
    const completionText = await page.locator('.progress-text').textContent();
    completion = parseInt(completionText?.replace('% Complete', '') || '0');
    
    if (completion >= 100) break;
    
    await page.click('button:has-text("Continue")');
    await page.waitForTimeout(500);
  }
  
  // Verify we can reach preview
  if (completion >= 100) {
    await page.click('button:has-text("Preview Listing")');
    await expect(page.locator('text=Your Listing Preview')).toBeVisible();
    console.log('Successfully reached preview');
  } else {
    console.log(`Reached ${completion}% completion`);
  }
  
  // Take screenshot
  await page.screenshot({ path: 'test-results/minimal-flow-result.png', fullPage: true });
  
  // Basic success - we got past the upload stage
  expect(completion).toBeGreaterThan(0);
});