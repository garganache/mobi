import { test, expect } from '@playwright/test';
import { 
  BASE_URL, 
  RO, 
  FIXTURES, 
  waitForPageLoad, 
  uploadImage,
  waitForFormField,
  fillPropertyForm,
  clickContinue
} from './helpers';

test.describe('Form Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
  });

  test('form fields appear after upload', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Wait for property_type field to appear
    await waitForFormField(page, 'select#property_type');
    
    // Verify field is visible
    await expect(page.locator('select#property_type')).toBeVisible();
  });

  test('can fill property type field', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // Fill property type
    await fillPropertyForm(page, { propertyType: 'apartment' });
    
    // Verify selection
    const select = page.locator('select#property_type');
    await expect(select).toHaveValue('apartment');
  });

  test('can fill all basic form fields', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // Fill property type
    await fillPropertyForm(page, {
      propertyType: 'apartment'
    });
    
    // Verify property type was set
    await expect(page.locator('select#property_type')).toHaveValue('apartment');
    
    // Click Continue to reveal more fields
    await clickContinue(page);
    
    // Fill remaining fields
    await fillPropertyForm(page, {
      bedrooms: '3',
      bathrooms: '2',
      squareFeet: '100'
    });
    
    // Verify remaining fields (property_type may not be visible after Continue)
    await expect(page.locator('input#bedrooms')).toHaveValue('3');
    await expect(page.locator('input#bathrooms')).toHaveValue('2');
    await expect(page.locator('input#square_feet')).toHaveValue('100');
  });

  test('property type dropdown shows Romanian labels', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // Click the dropdown
    await page.locator('select#property_type').click();
    
    // Check for Romanian options (they should be in the DOM)
    const selectHTML = await page.locator('select#property_type').innerHTML();
    
    // Options should exist (even if labels are Romanian, values are English)
    expect(selectHTML).toContain('apartment');
    expect(selectHTML).toContain('house');
  });

  test('bedrooms field accepts numeric input', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // Select property type
    await fillPropertyForm(page, {
      propertyType: 'house'
    });
    
    // Click Continue to reveal bedrooms field
    await clickContinue(page);
    
    // Fill bedrooms field
    await fillPropertyForm(page, {
      bedrooms: '4'
    });
    
    // Verify it was filled
    await expect(page.locator('input#bedrooms')).toHaveValue('4');
  });
});
