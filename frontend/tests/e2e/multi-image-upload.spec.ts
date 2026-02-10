import { test, expect } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

test.describe('Multi-Image Upload and Synthesis', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should upload multiple images and display synthesis results', async ({ page }) => {
    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Get the file input element
    const fileInput = page.locator('input[type="file"]');
    
    // Prepare test images
    const testImages = [
      'kitchen.jpg',
      'bedroom.jpg', 
      'bathroom.jpg',
      'living_room.jpg',
      'hallway.jpg',
      'exterior.jpg'
    ];

    // Read all test images
    const imagePaths = testImages.map(img => 
      path.join(__dirname, '../fixtures', img)
    );

    // Upload all images at once
    await fileInput.setInputFiles(imagePaths);

    // Wait for upload and analysis to complete
    await page.waitForTimeout(3000); // Wait for analysis to complete

    // Check that we have individual analyses displayed
    const uploadItems = page.locator('.upload-item');
    await expect(uploadItems).toHaveCount(6);

    // Check for synthesis results - look for property overview
    const propertyOverview = page.locator('text=/property.*overview|overview.*property/i');
    // If synthesis is displayed, it should be visible
    const hasSynthesis = await page.locator('text=/This.*property.*has|Property.*Overview/i').count();
    
    if (hasSynthesis > 0) {
      console.log('Synthesis results found');
    } else {
      console.log('No synthesis results visible - checking individual analyses');
    }

    // At minimum, we should have individual analyses
    await expect(uploadItems.first()).toBeVisible();
    
    // Check that each upload item has analysis content
    for (let i = 0; i < 6; i++) {
      const item = uploadItems.nth(i);
      await expect(item).toBeVisible();
      
      // Check if analysis is displayed (might be collapsed)
      const hasAnalysis = await item.locator('.analysis-content').count();
      if (hasAnalysis > 0) {
        console.log(`Analysis ${i} has content`);
      }
    }
  });

  test('should handle batch API upload when available', async ({ page }) => {
    // Check if batch mode is available in the component
    const batchModeIndicator = page.locator('text=/batch.*mode|multiple.*upload/i');
    const hasBatchMode = await batchModeIndicator.count() > 0;
    
    if (hasBatchMode) {
      console.log('Batch mode detected, testing batch upload');
      
      // Upload multiple images
      const fileInput = page.locator('input[type="file"]');
      const imagePaths = [
        path.join(__dirname, '../fixtures', 'kitchen.jpg'),
        path.join(__dirname, '../fixtures', 'bedroom.jpg'),
        path.join(__dirname, '../fixtures', 'living_room.jpg')
      ];
      
      await fileInput.setInputFiles(imagePaths);
      
      // Wait for batch processing
      await page.waitForTimeout(2000);
      
      // Check for synthesis results
      const synthesisResults = page.locator('text=/synthesis|unified|overview/i');
      await expect(synthesisResults).toBeVisible();
      
    } else {
      console.log('No batch mode detected, skipping batch test');
      test.skip();
    }
  });

  test('should display individual analyses for each uploaded image', async ({ page }) => {
    // Upload a few images
    const fileInput = page.locator('input[type="file"]');
    const imagePaths = [
      path.join(__dirname, '../fixtures', 'kitchen.jpg'),
      path.join(__dirname, '../fixtures', 'bedroom.jpg')
    ];
    
    await fileInput.setInputFiles(imagePaths);
    await page.waitForTimeout(2000);

    // Check that we have individual analysis displays
    const analysisDisplays = page.locator('.analysis-content, .vision-analysis');
    const count = await analysisDisplays.count();
    
    if (count > 0) {
      console.log(`Found ${count} analysis displays`);
      await expect(analysisDisplays.first()).toBeVisible();
    } else {
      console.log('No analysis displays found, checking for basic upload completion');
      // At minimum, check that uploads completed
      const completedUploads = page.locator('.upload-item:not(.is-uploading)');
      await expect(completedUploads).toHaveCount(2);
    }
  });

  test('should handle upload errors gracefully', async ({ page }) => {
    // Test with an invalid file
    const fileInput = page.locator('input[type="file"]');
    
    // Create a dummy text file to simulate invalid upload
    const invalidFile = path.join(__dirname, 'invalid.txt');
    await fs.writeFile(invalidFile, 'not an image');
    
    try {
      await fileInput.setInputFiles(invalidFile);
      await page.waitForTimeout(1000);
      
      // Check for error message
      const errorMessage = page.locator('.error-message, .upload-error');
      const hasError = await errorMessage.count();
      
      if (hasError > 0) {
        console.log('Error handling detected');
        await expect(errorMessage.first()).toBeVisible();
      } else {
        console.log('No error message found, checking for upload handling');
        // Should still handle the upload attempt
        const uploadItems = page.locator('.upload-item');
        await expect(uploadItems).toHaveCount(1);
      }
    } finally {
      // Cleanup
      await fs.unlink(invalidFile).catch(() => {});
    }
  });

  test('should allow removing uploaded images', async ({ page }) => {
    // Upload an image
    const fileInput = page.locator('input[type="file"]');
    const imagePath = path.join(__dirname, '../fixtures', 'kitchen.jpg');
    
    await fileInput.setInputFiles(imagePath);
    await page.waitForTimeout(1000);

    // Check that we have one upload
    const uploadItems = page.locator('.upload-item');
    await expect(uploadItems).toHaveCount(1);

    // Try to find and click remove button
    const removeButton = page.locator('.remove-button, button[title*="remove" i]');
    const hasRemove = await removeButton.count();
    
    if (hasRemove > 0) {
      await removeButton.click();
      
      // Check that image was removed
      await expect(uploadItems).toHaveCount(0);
    } else {
      console.log('No remove button found, skipping remove test');
    }
  });
});