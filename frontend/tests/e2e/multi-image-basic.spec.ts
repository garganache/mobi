import { test, expect } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Multi-Image Upload Basic Test', () => {
  test('should upload single image successfully', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Get the file input element
    const fileInput = page.locator('input[type="file"]');
    
    // Upload a single test image
    const imagePath = path.join(__dirname, '../fixtures/kitchen.jpg');
    await fileInput.setInputFiles(imagePath);
    
    // Wait for upload and analysis
    await page.waitForTimeout(3000);
    
    // Check that we have one upload item
    const uploadItems = page.locator('.upload-item');
    await expect(uploadItems).toHaveCount(1);
    
    console.log('Single image upload test passed!');
  });

  test('should upload multiple images', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Get the file input element
    const fileInput = page.locator('input[type="file"]');
    
    // Upload multiple test images
    const imagePaths = [
      path.join(__dirname, '../fixtures/kitchen.jpg'),
      path.join(__dirname, '../fixtures/bedroom.jpg'),
      path.join(__dirname, '../fixtures/living_room.jpg')
    ];
    
    await fileInput.setInputFiles(imagePaths);
    
    // Wait for upload and analysis
    await page.waitForTimeout(5000);
    
    // Check that we have multiple upload items
    const uploadItems = page.locator('.upload-item');
    const count = await uploadItems.count();
    expect(count).toBeGreaterThanOrEqual(3);
    
    console.log(`Multi-image upload test passed! Found ${count} items`);
  });
});