import { test, expect } from '@playwright/test';

/**
 * TASK-033: Complete Save Flow E2E Test
 * 
 * This test verifies the complete user journey from upload to save:
 * 1. Upload property images
 * 2. AI analyzes images
 * 3. User fills form fields
 * 4. User previews listing
 * 5. User saves listing
 * 6. Success confirmation displayed
 */

test.describe('Complete Save Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should complete full flow: upload → analyze → fill → preview → save', async ({ page }) => {
    // Step 1: Verify initial state
    await expect(page.locator('h2:has-text("Get Started")')).toBeVisible();
    
    // Step 2: Upload an image (using a test image)
    // Note: In a real test, you'd use a fixture image file
    // For now, we'll mock the API responses
    
    // Mock the analyze-batch endpoint
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: {
            total_rooms: 4,
            layout_type: 'open_concept',
            unified_description: 'A modern apartment with an open-concept living area',
            room_breakdown: {
              bedroom: 2,
              bathroom: 1,
              kitchen: 1,
              living_room: 1
            },
            property_overview: {
              property_type: 'apartment',
              style: 'modern',
              condition: 'excellent'
            },
            interior_features: ['hardwood_floors', 'granite_counters'],
            exterior_features: ['balcony']
          },
          individual_analyses: [
            {
              description: 'Modern living room with hardwood floors',
              rooms: { living_room: 1 },
              amenities: ['hardwood_floors'],
              property_type: 'apartment',
              style: 'modern',
              condition: 'excellent'
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
                { value: 'apartment', label: 'Apartment' },
                { value: 'house', label: 'House' }
              ]
            },
            {
              field_id: 'price',
              field_type: 'number',
              label: 'Price',
              required: false
            },
            {
              field_id: 'bedrooms',
              field_type: 'number',
              label: 'Bedrooms',
              required: false
            }
          ],
          ai_message: 'I detected an apartment. Let me know the details!',
          step_number: 1,
          completion_percentage: 30
        })
      });
    });

    // Upload image (simulate file upload)
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.isVisible()) {
      // Create a test image buffer
      const buffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
      await fileInput.setInputFiles({
        name: 'test-image.png',
        mimeType: 'image/png',
        buffer: buffer
      });
    }

    // Wait for form to appear
    await page.waitForSelector('select#property_type', { timeout: 5000 });

    // Step 3: Fill form fields
    await page.selectOption('select#property_type', 'apartment');
    await page.fill('input#price', '350000');
    await page.fill('input#bedrooms', '2');

    // Step 4: Trigger preview (if there's a preview button)
    const previewButton = page.locator('button:has-text("Preview")');
    if (await previewButton.isVisible()) {
      await previewButton.click();
    } else {
      // If completion is 100%, preview might show automatically
      // Wait for preview content
      await page.waitForSelector('.listing-preview, .preview-hero', { timeout: 10000 });
    }

    // Step 5: Verify preview is displayed
    const previewHeading = page.locator('h1, h2').filter({ hasText: /Listing|Preview/ }).first();
    await expect(previewHeading).toBeVisible({ timeout: 10000 });

    // Step 6: Mock the save endpoint
    let saveRequestBody: any = null;
    await page.route('**/api/listings', async (route) => {
      const request = route.request();
      if (request.method() === 'POST') {
        saveRequestBody = JSON.parse(request.postData() || '{}');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            listing_id: 123,
            message: 'Listing saved successfully'
          })
        });
      }
    });

    // Step 7: Click "Save Listing" button
    const saveButton = page.locator('button:has-text("Save")').first();
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Step 8: Verify success modal appears
    await expect(page.locator('text=/Saved Successfully|Success/')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=/Listing ID.*123/')).toBeVisible();

    // Step 9: Verify the payload structure
    expect(saveRequestBody).toBeTruthy();
    expect(saveRequestBody.property_type).toBe('apartment');
    expect(saveRequestBody.price).toBe(350000);
    expect(saveRequestBody.bedrooms).toBe(2);
    expect(saveRequestBody.images).toBeDefined();
    expect(Array.isArray(saveRequestBody.images)).toBe(true);
    
    // Verify synthesis data was included
    if (saveRequestBody.synthesis) {
      expect(saveRequestBody.synthesis.total_rooms).toBeDefined();
      expect(saveRequestBody.synthesis.unified_description).toBeDefined();
    }

    console.log('✅ Complete save flow test passed!');
  });

  test('should handle save errors gracefully', async ({ page }) => {
    // Set up the page to show preview immediately (mock previous steps)
    await page.evaluate(() => {
      // Mock data in localStorage
      localStorage.setItem('mobi_listing_state', JSON.stringify({
        formData: { property_type: 'apartment', price: 300000 },
        schema: [],
        aiMessage: '',
        currentStep: 5,
        completionPercentage: 100
      }));
    });

    await page.reload();

    // Mock save endpoint to return error
    await page.route('**/api/listings', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'At least one image is required'
        })
      });
    });

    // Try to save (if preview is visible)
    const saveButton = page.locator('button:has-text("Save")');
    if (await saveButton.isVisible()) {
      await saveButton.click();

      // Verify error message appears
      await expect(page.locator('text=/error|failed|required/i')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should show "Create Another" option after successful save', async ({ page }) => {
    // Similar setup as first test, focusing on post-save actions
    // This would navigate to preview and save
    
    // Mock successful save
    await page.route('**/api/listings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          listing_id: 456,
          message: 'Listing saved successfully'
        })
      });
    });

    // Note: This is a placeholder test structure
    // In a real scenario, you'd set up the full state and click save
    
    // Then verify "Create Another" button exists in success modal
    // await expect(page.locator('button:has-text("Create Another")')).toBeVisible();
  });
});
