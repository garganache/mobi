import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test('simple save flow test', async ({ page }) => {
  // Navigate to app
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  
  // Wait for the landing page
  await expect(page.locator('text=Drop a photo to start your listing')).toBeVisible();
  
  // Upload single image
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
  
  // Wait for AI response
  await expect(page.locator('text=Let\'s start by identifying what type of property you\'re listing.')).toBeVisible({ timeout: 30000 });
  
  // Fill property type
  await page.locator('select[name="property_type"]').selectOption('apartment');
  
  // Fill some basic fields
  await page.fill('input[name="bedrooms"]', '2');
  
  // Click Continue to progress
  await page.click('button:has-text("Continue")');
  
  // Wait for more fields to appear
  await expect(page.locator('text=100% Complete')).toBeVisible({ timeout: 10000 });
  
  // Go to preview
  await page.click('button:has-text("Preview Listing")');
  
  // Verify preview page
  await expect(page.locator('text=Your Listing Preview')).toBeVisible();
  
  // Click Save/Publish button
  await page.click('button:has-text("Publish Listing")');
  
  // Wait for success modal
  await expect(page.locator('text=Listing Saved Successfully')).toBeVisible({ timeout: 10000 });
  
  console.log('Save flow test completed successfully!');
});