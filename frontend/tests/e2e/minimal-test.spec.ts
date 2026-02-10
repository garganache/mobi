import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('Minimal UI Discovery Test', () => {
  test('discover actual UI elements', async ({ page }) => {
    // Navigate to app
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Take initial screenshot
    await page.screenshot({ path: 'test-results/initial-landing.png', fullPage: true });
    
    // Check what's actually on the page
    const headingText = await page.locator('h1').textContent();
    console.log('Main heading:', headingText);
    
    const h2Text = await page.locator('h2').textContent();
    console.log('H2 text:', h2Text);
    
    // Look for any text containing "upload" or "photo"
    const pageText = await page.textContent('body');
    console.log('Page text contains "upload":', pageText?.toLowerCase().includes('upload'));
    console.log('Page text contains "photo":', pageText?.toLowerCase().includes('photo'));
    console.log('Page text contains "listing":', pageText?.toLowerCase().includes('listing'));
    
    // Check for file input
    const fileInput = page.locator('input[type="file"]');
    const fileInputCount = await fileInput.count();
    console.log('Number of file inputs:', fileInputCount);
    
    // Check for buttons
    const buttons = await page.locator('button').allTextContents();
    console.log('Button texts:', buttons);
    
    // Check for any upload area or drag/drop zone
    const uploadAreas = page.locator('[class*="upload"], [id*="upload"]');
    const uploadAreaCount = await uploadAreas.count();
    console.log('Upload areas found:', uploadAreaCount);
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'test-results/debug-discovery.png', fullPage: true });
    
    // Try to upload a simple image
    if (fileInputCount > 0) {
      console.log('Attempting to upload image...');
      await fileInput.first().setInputFiles('tests/fixtures/kitchen.jpg');
      
      // Wait a bit and see what changes
      await page.waitForTimeout(3000);
      
      // Take screenshot after upload
      await page.screenshot({ path: 'test-results/after-upload.png', fullPage: true });
      
      // Check what changed
      const newPageText = await page.textContent('body');
      console.log('Page text after upload contains "Property":', newPageText?.toLowerCase().includes('property'));
      console.log('Page text after upload contains "Overview":', newPageText?.toLowerCase().includes('overview'));
    }
    
    // Final discovery screenshot
    await page.screenshot({ path: 'test-results/final-discovery.png', fullPage: true });
    
    // Basic assertion to make sure page loaded
    expect(headingText).toBeTruthy();
  });
});