import { test, expect } from '@playwright/test';
import { 
  BASE_URL, 
  RO, 
  FIXTURES, 
  waitForPageLoad, 
  uploadImage,
  uploadMultipleImages,
  verifyUploadedImages 
} from './helpers';

test.describe('Image Upload', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
  });

  test('uploads single image successfully', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Verify image was uploaded by checking for upload confirmation
    await verifyUploadedImages(page, 1);
    
    // Success is confirmed by the property overview section appearing
    // (buttons may be out of view or require scrolling)
    await expect(page.locator('h5:has-text("Imagine 1")')).toBeVisible({ timeout: 10000 });
  });

  test('uploads multiple images', async ({ page }) => {
    await uploadMultipleImages(page, [
      FIXTURES.KITCHEN,
      FIXTURES.BEDROOM,
      FIXTURES.LIVING_ROOM
    ]);
    
    // Verify all images were uploaded
    await verifyUploadedImages(page, 3);
    
    // Verify Continue button appears
    await expect(page.locator(`button:has-text("${RO.CONTINUE}")`)).toBeVisible({ timeout: 10000 });
  });

  test('displays uploaded image analysis', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Check for image analysis section with "Imagine 1"
    await expect(page.locator('h5:has-text("Imagine 1")')).toBeVisible({ timeout: 10000 });
    
    // Check for "Prezentare Proprietate" section
    await expect(page.locator('h3:has-text("Prezentare Proprietate")')).toBeVisible({ timeout: 10000 });
  });

  test('shows file name after upload', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Check for filename display
    await expect(page.locator('text=kitchen.jpg')).toBeVisible({ timeout: 10000 });
  });
});
