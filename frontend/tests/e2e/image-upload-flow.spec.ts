import { test, expect } from '@playwright/test';
import path from 'path';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test.describe('Image Upload Flow Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('Upload via drag-and-drop', async ({ page }) => {
    // Wait for the drop zone to be visible
    const dropZone = page.locator('[data-testid="image-drop-zone"]');
    await expect(dropZone).toBeVisible();
    
    // Create a test image file
    const testImagePath = path.join(__dirname, '../fixtures/test-image.jpg');
    
    // Drag and drop the file
    await dropZone.dragAndDrop({
      files: [{
        name: 'test-image.jpg',
        mimeType: 'image/jpeg',
        buffer: Buffer.from('test image data')
      }]
    });
    
    // Verify upload is triggered
    await expect(page.locator('text=Uploading...')).toBeVisible();
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
  });

  test('Upload via file picker', async ({ page }) => {
    // Click the upload button
    const uploadButton = page.locator('button:has-text("Upload Image")');
    await uploadButton.click();
    
    // Wait for file input and upload
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/test-image.jpg');
    
    // Verify upload process
    await expect(page.locator('text=Uploading...')).toBeVisible();
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
  });

  test('Image preview displays', async ({ page }) => {
    // Upload an image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/test-image.jpg');
    
    // Wait for upload and preview
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    
    // Verify image preview appears
    const imagePreview = page.locator('[data-testid="image-preview"] img');
    await expect(imagePreview).toBeVisible();
    await expect(imagePreview).toHaveAttribute('src', /blob:.*test-image/);
  });

  test('Loading state shows during processing', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/test-image.jpg');
    
    // Verify loading state appears immediately
    const loadingIndicator = page.locator('[data-testid="loading-indicator"]');
    await expect(loadingIndicator).toBeVisible();
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    
    // Verify loading state disappears after processing
    await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
  });

  test('Valid file types accepted', async ({ page }) => {
    const validTypes = ['jpg', 'jpeg', 'png', 'webp'];
    
    for (const type of validTypes) {
      await page.goto(BASE_URL, { waitUntil: 'networkidle' });
      
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(`tests/fixtures/test-image.${type}`);
      
      // Verify upload starts without error
      await expect(page.locator('text=Uploading...')).toBeVisible();
      await expect(page.locator(`text=Invalid file type`)).not.toBeVisible();
      
      // Wait for analysis to complete
      await page.waitForTimeout(2000); // Brief wait for processing
    }
  });

  test('Invalid file types rejected with error message', async ({ page }) => {
    const invalidTypes = ['pdf', 'txt', 'doc', 'mp4'];
    
    for (const type of invalidTypes) {
      await page.goto(BASE_URL, { waitUntil: 'networkidle' });
      
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(`tests/fixtures/test-file.${type}`);
      
      // Verify error message appears
      await expect(page.locator(`text=Invalid file type`)).toBeVisible();
      await expect(page.locator(`text=Please upload an image file (JPG, PNG, or WebP)`)).toBeVisible();
    }
  });

  test('File size limit enforced', async ({ page }) => {
    // Upload a large file (simulate 10MB+)
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/large-image.jpg');
    
    // Verify size limit error
    await expect(page.locator('text=File too large')).toBeVisible();
    await expect(page.locator('text=Maximum file size is 5MB')).toBeVisible();
  });

  test('Multiple images can be uploaded sequentially', async ({ page }) => {
    // Upload first image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for first analysis
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    await expect(page.locator('text=I see a kitchen!')).toBeVisible({ timeout: 10000 });
    
    // Upload second image
    await fileInput.setInputFiles('tests/fixtures/bedroom.jpg');
    
    // Verify second analysis
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    await expect(page.locator('text=I see a bedroom!')).toBeVisible({ timeout: 10000 });
    
    // Upload third image
    await fileInput.setInputFiles('tests/fixtures/exterior.jpg');
    
    // Verify third analysis
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    await expect(page.locator('text=I see the exterior!')).toBeVisible({ timeout: 10000 });
    
    // Verify all images are displayed
    const uploadedImages = page.locator('[data-testid="uploaded-image"]');
    await expect(uploadedImages).toHaveCount(3);
  });

  test('Visual regression: Upload UI states', async ({ page }) => {
    // Initial state
    await page.screenshot({ path: 'tests/screenshots/upload-initial.png', fullPage: true });
    
    // Hover state
    const dropZone = page.locator('[data-testid="image-drop-zone"]');
    await dropZone.hover();
    await page.screenshot({ path: 'tests/screenshots/upload-hover.png', fullPage: true });
    
    // Uploading state
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/test-image.jpg');
    await page.screenshot({ path: 'tests/screenshots/upload-loading.png', fullPage: true });
    
    // Success state
    await expect(page.locator('text=I see a')).toBeVisible({ timeout: 10000 });
    await page.screenshot({ path: 'tests/screenshots/upload-success.png', fullPage: true });
  });
});