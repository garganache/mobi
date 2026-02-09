import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test.describe('Complete User Journey E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('Happy Path: Upload image → AI detects features → progressive field reveal → complete listing', async ({ page }) => {
    // Wait for the landing page to load
    await expect(page.locator('text=Drop a photo to start your listing')).toBeVisible();
    
    // Upload an image of a kitchen
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Verify loading state appears
    await expect(page.locator('text=Analyzing your image...')).toBeVisible();
    
    // Wait for AI response
    await expect(page.locator('text=I see a modern kitchen! Is this a house or an apartment?')).toBeVisible({ timeout: 10000 });
    
    // Select property type
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Verify that 2-3 relevant fields appear progressively
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    await expect(page.locator('label:has-text("Square Footage")')).toBeVisible();
    
    // Fill in the fields
    await page.locator('input[name="bedrooms"]').fill('2');
    await page.locator('input[name="square_footage"]').fill('1200');
    
    // Verify more fields appear as user progresses
    await expect(page.locator('label:has-text("Monthly Rent")')).toBeVisible();
    
    // Complete the listing
    await page.locator('input[name="rent"]').fill('2500');
    
    // Verify listing is complete
    await expect(page.locator('text=Listing created successfully!')).toBeVisible();
    
    // Take screenshot for documentation
    await page.screenshot({ path: 'tests/screenshots/happy-path-complete.png', fullPage: true });
  });

  test('Multiple Images: Upload multiple images and accumulate fields', async ({ page }) => {
    // Wait for the landing page
    await expect(page.locator('text=Drop a photo to start your listing')).toBeVisible();
    
    // Upload first image (kitchen)
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for AI analysis
    await expect(page.locator('text=I see a modern kitchen!')).toBeVisible({ timeout: 10000 });
    
    // Fill suggested fields
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.locator('input[name="bedrooms"]').fill('2');
    
    // Upload second image (living room)
    await fileInput.setInputFiles('tests/fixtures/living-room.jpg');
    
    // Verify new fields appear based on second image
    await expect(page.locator('text=I see a spacious living area!')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('label:has-text("Has Fireplace")')).toBeVisible();
    
    // Complete the listing with accumulated fields
    await page.locator('input[name="has_fireplace"]').check();
    await page.locator('input[name="rent"]').fill('2800');
    
    // Verify completion
    await expect(page.locator('text=Listing created successfully!')).toBeVisible();
    
    await page.screenshot({ path: 'tests/screenshots/multiple-images-complete.png', fullPage: true });
  });

  test('Low Confidence: AI asks clarifying questions', async ({ page }) => {
    // Upload unclear image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/blurry-image.jpg');
    
    // Wait for AI to ask for clarification
    await expect(page.locator('text=This image is a bit unclear')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Could you tell me what type of property this is?')).toBeVisible();
    
    // User provides info
    await page.locator('select[name="property_type"]').selectOption('house');
    
    // Verify flow continues
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    
    await page.screenshot({ path: 'tests/screenshots/low-confidence-clarification.png', fullPage: true });
  });

  test('Wrong Detection: User corrects AI and form adjusts', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/bedroom.jpg');
    
    // AI incorrectly detects as kitchen
    await expect(page.locator('text=I see a kitchen!')).toBeVisible({ timeout: 10000 });
    
    // User corrects the AI
    await page.locator('button:has-text("This isn\'t a kitchen")').click();
    
    // Verify form adjusts based on correction
    await expect(page.locator('text=Let me take another look...')).toBeVisible();
    await expect(page.locator('label:has-text("This appears to be a bedroom")')).toBeVisible();
    
    // Continue with corrected information
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    
    await page.screenshot({ path: 'tests/screenshots/wrong-detection-corrected.png', fullPage: true });
  });

  test('Performance: Measure key metrics', async ({ page }) => {
    const startTime = Date.now();
    
    // Upload image and measure time to first field
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    const firstFieldStart = Date.now();
    await expect(page.locator('select[name="property_type"]')).toBeVisible({ timeout: 10000 });
    const timeToFirstField = Date.now() - firstFieldStart;
    
    // Complete the form and measure total time
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.locator('input[name="bedrooms"]').fill('2');
    await page.locator('input[name="square_footage"]').fill('1200');
    await page.locator('input[name="rent"]').fill('2500');
    
    await expect(page.locator('text=Listing created successfully!')).toBeVisible();
    const totalTime = Date.now() - startTime;
    
    // Log performance metrics
    console.log(`Performance Metrics:
      - Time to first field: ${timeToFirstField}ms
      - Total completion time: ${totalTime}ms
    `);
    
    // Assert reasonable performance (adjust thresholds as needed)
    expect(timeToFirstField).toBeLessThan(5000); // 5 seconds max to first field
    expect(totalTime).toBeLessThan(30000); // 30 seconds max total
  });
});