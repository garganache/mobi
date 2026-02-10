import { test, expect } from '@playwright/test';

/**
 * Test: Reset Form Functionality
 * 
 * Verifies that the reset button clears all data:
 * - Form fields
 * - Uploaded images
 * - Synthesis data (property overview)
 * - Individual analyses
 * - Completion percentage
 * - Returns to initial upload state
 */

test.describe('Reset Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should clear all data and return to initial state when reset clicked', async ({ page }) => {
    // Mock the analyze-batch endpoint
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: {
            total_rooms: 3,
            layout_type: 'traditional',
            unified_description: 'A cozy traditional home',
            room_breakdown: {
              bedroom: 2,
              bathroom: 1
            },
            property_overview: {
              property_type: 'house',
              style: 'traditional',
              condition: 'good'
            },
            interior_features: ['hardwood_floors'],
            exterior_features: ['porch']
          },
          individual_analyses: [
            {
              description: 'Bedroom with hardwood floors',
              rooms: { bedroom: 1 },
              amenities: ['hardwood_floors'],
              property_type: 'house'
            }
          ]
        })
      });
    });

    // Mock the analyze-step endpoint
    await page.route('**/api/analyze-step', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          extracted_data: {},
          ui_schema: [
            {
              field_id: 'property_type',
              field_type: 'select',
              label: 'Property Type',
              required: true,
              options: [
                { value: 'house', label: 'House' },
                { value: 'apartment', label: 'Apartment' }
              ]
            },
            {
              field_id: 'price',
              field_type: 'number',
              label: 'Price'
            }
          ],
          ai_message: 'Please provide property details',
          step_number: 1,
          completion_percentage: 25
        })
      });
    });

    // Step 1: Verify initial state
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();

    // Step 2: Upload an image
    const fileInput = page.locator('input[type="file"]');
    const buffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    await fileInput.setInputFiles({
      name: 'test-house.png',
      mimeType: 'image/png',
      buffer: buffer
    });

    // Step 3: Wait for synthesis/property overview to appear
    await page.waitForSelector('text=/Property Overview|total rooms/i', { timeout: 5000 });

    // Step 4: Fill property type field
    await page.waitForSelector('select#property_type', { timeout: 5000 });
    await page.selectOption('select#property_type', 'house');

    // Step 5: Fill price field
    await page.waitForSelector('input#price', { timeout: 5000 });
    await page.fill('input#price', '450000');

    // Step 6: Verify data is present before reset
    // - Property overview should be visible
    const propertyOverview = page.locator('text=/Property Overview|total rooms|traditional/i');
    await expect(propertyOverview).toBeVisible();

    // - Form fields should have values
    const propertyTypeField = page.locator('select#property_type');
    await expect(propertyTypeField).toHaveValue('house');
    
    const priceField = page.locator('input#price');
    await expect(priceField).toHaveValue('450000');

    // Step 7: Click reset button
    const resetButton = page.locator('button[title="Reset form"]');
    await expect(resetButton).toBeVisible();

    // Handle the confirmation dialog
    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('confirm');
      expect(dialog.message()).toContain('Are you sure');
      await dialog.accept();
    });

    await resetButton.click();

    // Step 8: Verify everything is cleared
    // Wait a bit for state to update
    await page.waitForTimeout(500);

    // Should be back to initial state - "Get Started" visible
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible({ timeout: 2000 });

    // Property overview should be gone
    await expect(propertyOverview).not.toBeVisible();

    // Form fields should not exist (no schema)
    await expect(page.locator('select#property_type')).not.toBeVisible();
    await expect(page.locator('input#price')).not.toBeVisible();

    // Upload section should be visible again
    const uploadInput = page.locator('input[type="file"]');
    await expect(uploadInput).toBeVisible();
  });

  test('should not reset if user cancels confirmation dialog', async ({ page }) => {
    // Mock endpoints
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: {
            total_rooms: 2,
            layout_type: 'open_concept',
            unified_description: 'Modern apartment',
            room_breakdown: { bedroom: 1, bathroom: 1 },
            property_overview: {},
            interior_features: [],
            exterior_features: []
          },
          individual_analyses: []
        })
      });
    });

    await page.route('**/api/analyze-step', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          extracted_data: {},
          ui_schema: [
            {
              field_id: 'property_type',
              field_type: 'select',
              label: 'Property Type',
              options: [{ value: 'apartment', label: 'Apartment' }]
            }
          ],
          ai_message: 'Property details',
          step_number: 1,
          completion_percentage: 20
        })
      });
    });

    // Upload image and fill data
    const fileInput = page.locator('input[type="file"]');
    const buffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    await fileInput.setInputFiles({
      name: 'test.png',
      mimeType: 'image/png',
      buffer: buffer
    });

    await page.waitForSelector('select#property_type', { timeout: 5000 });
    await page.selectOption('select#property_type', 'apartment');

    // Verify data is there
    const propertyTypeField = page.locator('select#property_type');
    await expect(propertyTypeField).toHaveValue('apartment');

    // Click reset but cancel
    const resetButton = page.locator('button[title="Reset form"]');

    page.on('dialog', async dialog => {
      expect(dialog.type()).toBe('confirm');
      await dialog.dismiss(); // Cancel
    });

    await resetButton.click();

    // Wait a bit
    await page.waitForTimeout(500);

    // Data should still be there
    await expect(propertyTypeField).toBeVisible();
    await expect(propertyTypeField).toHaveValue('apartment');

    // Should NOT be back to initial state
    await expect(page.locator('h2:has-text("Get Started")')).not.toBeVisible();
  });

  test('should clear localStorage when reset', async ({ page }) => {
    // Mock endpoints
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: { total_rooms: 1, layout_type: 'studio', unified_description: 'Studio', room_breakdown: {}, property_overview: {}, interior_features: [], exterior_features: [] },
          individual_analyses: []
        })
      });
    });

    // Upload and trigger some state
    const fileInput = page.locator('input[type="file"]');
    const buffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    await fileInput.setInputFiles({
      name: 'test.png',
      mimeType: 'image/png',
      buffer: buffer
    });

    await page.waitForTimeout(1000);

    // Verify localStorage has data
    const localStorageBefore = await page.evaluate(() => {
      return localStorage.getItem('mobi_listing_state');
    });
    expect(localStorageBefore).not.toBeNull();

    // Click reset
    const resetButton = page.locator('button[title="Reset form"]');
    page.on('dialog', async dialog => {
      await dialog.accept();
    });
    await resetButton.click();

    await page.waitForTimeout(500);

    // Verify localStorage is cleared
    const localStorageAfter = await page.evaluate(() => {
      return localStorage.getItem('mobi_listing_state');
    });
    expect(localStorageAfter).toBeNull();
  });
});
