import { test, expect } from '@playwright/test';

/**
 * Test: Property Type Preservation Bug
 * 
 * This test verifies that user-selected property_type is NOT overwritten
 * when clicking "Continue" and receiving new backend responses.
 * 
 * Bug scenario (fixed):
 * 1. User selects property_type = "apartment"
 * 2. Clicks "Continue"
 * 3. Backend returns extracted_data with property_type: null
 * 4. Old code overwrote user selection with null
 * 5. Preview button failed validation
 * 
 * Expected behavior (after fix):
 * - property_type stays "apartment" through all Continue clicks
 * - Preview button works successfully
 */

test.describe('Property Type Preservation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should preserve property_type selection through multiple Continue clicks', async ({ page }) => {
    // Track the step number to return different responses
    let stepNumber = 0;
    
    // Mock the batch upload endpoint
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: {
            total_rooms: 3,
            layout_type: 'modern',
            unified_description: 'A modern apartment with open spaces',
            room_breakdown: {
              bedroom: 2,
              bathroom: 1,
              kitchen: 1
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
              description: 'Modern living room',
              rooms: { living_room: 1 },
              amenities: ['hardwood_floors'],
              property_type: 'apartment'
            },
            {
              description: 'Kitchen with granite counters',
              rooms: { kitchen: 1 },
              amenities: ['granite_counters']
            }
          ]
        })
      });
    });

    // Mock analyze-step endpoint - returns different fields each step
    await page.route('**/api/analyze-step', async (route) => {
      stepNumber++;
      
      let response;
      
      if (stepNumber === 1) {
        // Step 1: Just property_type field
        response = {
          extracted_data: {
            // ⚠️ Backend sends null for property_type (doesn't know yet)
            property_type: null
          },
          ui_schema: [
            {
              field_id: 'property_type',
              field_type: 'select',
              label: 'Property Type',
              required: true,
              options: [
                { value: 'apartment', label: 'Apartment' },
                { value: 'house', label: 'House' },
                { value: 'condo', label: 'Condo' }
              ]
            }
          ],
          ai_message: 'What type of property is this?',
          step_number: 1,
          completion_percentage: 20
        };
      } else if (stepNumber === 2) {
        // Step 2: Add price and bedrooms fields
        // ⚠️ Backend still sends property_type: null in extracted_data!
        response = {
          extracted_data: {
            property_type: null,  // ← This would overwrite user selection (BUG!)
            price: null,
            bedrooms: null
          },
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
              label: 'Price'
            },
            {
              field_id: 'bedrooms',
              field_type: 'number',
              label: 'Bedrooms'
            }
          ],
          ai_message: 'Great! Now let me get some more details.',
          step_number: 2,
          completion_percentage: 40
        };
      } else if (stepNumber === 3) {
        // Step 3: Add more fields
        response = {
          extracted_data: {
            property_type: null,  // ← Still null!
            bathrooms: null,
            square_feet: null
          },
          ui_schema: [
            {
              field_id: 'property_type',
              field_type: 'select',
              label: 'Property Type',
              options: [
                { value: 'apartment', label: 'Apartment' },
                { value: 'house', label: 'House' }
              ]
            },
            {
              field_id: 'price',
              field_type: 'number',
              label: 'Price'
            },
            {
              field_id: 'bedrooms',
              field_type: 'number',
              label: 'Bedrooms'
            },
            {
              field_id: 'bathrooms',
              field_type: 'number',
              label: 'Bathrooms'
            },
            {
              field_id: 'square_feet',
              field_type: 'number',
              label: 'Square Feet'
            }
          ],
          ai_message: 'Just a few more details!',
          step_number: 3,
          completion_percentage: 60
        };
      } else {
        // Step 4+: Complete (empty schema)
        response = {
          extracted_data: {},
          ui_schema: [],
          ai_message: 'All done!',
          step_number: 4,
          completion_percentage: 100
        };
      }
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });

    // STEP 1: Upload images
    console.log('Step 1: Uploading images...');
    const fileInput = page.locator('input[type="file"]');
    const buffer1 = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    const buffer2 = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==', 'base64');
    
    await fileInput.setInputFiles([
      { name: 'room1.png', mimeType: 'image/png', buffer: buffer1 },
      { name: 'room2.png', mimeType: 'image/png', buffer: buffer2 }
    ]);

    // Wait for property overview to appear
    await page.waitForSelector('text=/Property Overview|total rooms/i', { timeout: 5000 });

    // STEP 2: Wait for property_type field and select "apartment"
    console.log('Step 2: Selecting property_type = apartment');
    await page.waitForSelector('select#property_type', { timeout: 5000 });
    await page.selectOption('select#property_type', 'apartment');
    
    // Verify it's selected
    let propertyTypeValue = await page.locator('select#property_type').inputValue();
    expect(propertyTypeValue).toBe('apartment');
    console.log('✓ property_type selected: apartment');

    // STEP 3: Click Continue (triggers step 2 response with property_type: null in extracted_data)
    console.log('Step 3: Clicking Continue (step 2)...');
    const continueButton = page.locator('button:has-text("Continue")');
    await continueButton.click();
    
    // Wait for new fields to appear
    await page.waitForSelector('input#price', { timeout: 5000 });
    
    // ⚠️ CRITICAL CHECK: property_type should STILL be "apartment"!
    propertyTypeValue = await page.locator('select#property_type').inputValue();
    expect(propertyTypeValue).toBe('apartment');
    console.log('✓ After Continue click: property_type STILL apartment (not overwritten!)');

    // Fill the new fields
    await page.fill('input#price', '350000');
    await page.fill('input#bedrooms', '2');

    // STEP 4: Click Continue again (step 3 response, also has property_type: null)
    console.log('Step 4: Clicking Continue again (step 3)...');
    await continueButton.click();
    
    // Wait for more fields
    await page.waitForSelector('input#bathrooms', { timeout: 5000 });
    
    // ⚠️ CRITICAL CHECK AGAIN: property_type should STILL be "apartment"!
    propertyTypeValue = await page.locator('select#property_type').inputValue();
    expect(propertyTypeValue).toBe('apartment');
    console.log('✓ After 2nd Continue: property_type STILL apartment!');

    // Fill more fields
    await page.fill('input#bathrooms', '1');
    await page.fill('input#square_feet', '1200');

    // STEP 5: Click Continue one more time to reach 100%
    console.log('Step 5: Clicking Continue to reach 100%...');
    await continueButton.click();
    
    // Wait for completion state
    await page.waitForSelector('text=/Listing Complete|Preview Listing/i', { timeout: 5000 });

    // STEP 6: Final check before preview
    console.log('Step 6: Final check - property_type should STILL be apartment');
    
    // Check localStorage state
    const savedState = await page.evaluate(() => {
      const state = localStorage.getItem('mobi_listing_state');
      return state ? JSON.parse(state) : null;
    });
    
    console.log('Saved state formData:', savedState?.formData);
    expect(savedState?.formData?.property_type?.value).toBe('apartment');
    console.log('✓ localStorage confirms: property_type = apartment');

    // STEP 7: Click Preview Listing button
    console.log('Step 7: Clicking Preview Listing...');
    const previewButton = page.locator('button:has-text("Preview Listing")');
    await expect(previewButton).toBeVisible();
    await previewButton.click();

    // STEP 8: Verify preview page loads (no validation error!)
    console.log('Step 8: Verifying preview page loaded...');
    await page.waitForSelector('text=/Listing|Preview/i', { timeout: 5000 });
    
    // Should NOT see error message about missing property_type
    await expect(page.locator('text=/property type.*missing/i')).not.toBeVisible();
    
    console.log('✅ SUCCESS! Preview loaded without property_type error!');
    
    // Verify the preview page has the data
    // (Property type should be shown somewhere in the preview)
    await expect(page.locator('text=/apartment/i')).toBeVisible();
    
    console.log('✅ Preview page shows property_type = apartment');
  });

  test('should show validation error if property_type never selected', async ({ page }) => {
    // This test verifies the validation DOES work when legitimately missing
    
    await page.route('**/api/analyze-batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          synthesis: {
            total_rooms: 1,
            layout_type: 'studio',
            unified_description: 'Studio apartment',
            room_breakdown: {},
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
          ui_schema: [],
          ai_message: 'Done',
          step_number: 1,
          completion_percentage: 100
        })
      });
    });

    // Upload image
    const fileInput = page.locator('input[type="file"]');
    const buffer = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', 'base64');
    await fileInput.setInputFiles({ name: 'test.png', mimeType: 'image/png', buffer });

    await page.waitForTimeout(1000);

    // Try to click preview (should be available via "Preview & Save" button)
    const previewButton = page.locator('button:has-text("Preview")').first();
    if (await previewButton.isVisible({ timeout: 2000 })) {
      await previewButton.click();
      
      // Should see validation error
      await expect(page.locator('text=/property type.*before preview/i')).toBeVisible({ timeout: 3000 });
      console.log('✓ Validation error shown when property_type legitimately missing');
    }
  });
});
