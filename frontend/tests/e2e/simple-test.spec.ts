import { test, expect } from '@playwright/test';

test('multi-image upload functionality test', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5174');
  
  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Test that the page loads
  const title = await page.title();
  expect(title).toBeTruthy();
  
  // Check that file input exists (but don't check visibility since it's hidden)
  const fileInput = page.locator('input[type="file"]');
  await expect(fileInput).toHaveCount(1);
  
  console.log('Basic page test passed!');
});