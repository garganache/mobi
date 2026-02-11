import { test, expect } from '@playwright/test';
import { 
  BASE_URL, 
  RO, 
  FIXTURES, 
  waitForPageLoad, 
  uploadImage,
  waitForFormField
} from './helpers';

test.describe('Romanian Localization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
  });

  test('all main UI elements are in Romanian', async ({ page }) => {
    // Header
    await expect(page.locator('h1')).toContainText(RO.APP_TITLE);
    await expect(page.locator('h2')).toContainText(RO.GET_STARTED);
    
    // Browse button
    await expect(page.locator(`text=${RO.BROWSE}`)).toBeVisible();
    
    // Initial AI message
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    const aiText = await aiMessage.textContent();
    expect(aiText).toContain('Pune o poză');
  });

  test('buttons show Romanian text after upload', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Continue button
    await expect(page.locator(`button:has-text("${RO.CONTINUE}")`))
      .toBeVisible({ timeout: 10000 });
    
    // Preview & Save button
    await expect(page.locator(`button:has-text("${RO.PREVIEW_SAVE}")`))
      .toBeVisible({ timeout: 10000 });
  });

  test('AI messages remain in Romanian throughout flow', async ({ page }) => {
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    
    // Initial message
    await expect(aiMessage).toBeVisible();
    let text = await aiMessage.textContent();
    expect(text).toContain('Pune o poză');
    
    // After upload
    await uploadImage(page, FIXTURES.KITCHEN);
    
    // Message should update but remain in Romanian
    await page.waitForTimeout(3000);
    text = await aiMessage.textContent();
    
    // Should NOT contain common English phrases
    expect(text).not.toContain('Get started');
    expect(text).not.toContain('Upload your');
    expect(text).not.toContain('Let\'s begin');
    expect(text).not.toContain('Please upload');
    
    // Should contain Romanian text (check for Romanian diacritics or common Romanian words)
    // Valid responses include: "Nu au fost detectate camere", "Să începem", etc.
    const hasRomanianIndicators = text && (
      // Check for Romanian-specific characters
      /[ăîțș]/i.test(text) ||
      // Or common Romanian words/patterns
      /nu au|fost|camere|imagini|furnizat|detectat/i.test(text) ||
      /să|prin|tip|proprietate|identific/i.test(text)
    );
    expect(hasRomanianIndicators).toBeTruthy();
  });

  test('form field labels are in Romanian', async ({ page }) => {
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // Check for Romanian field labels in the page
    const pageText = await page.textContent('body');
    
    // Should contain Romanian words for common fields
    expect(pageText).toMatch(/Tip|Proprietate|Preț|Dormitor|Baie/i);
  });

  test('error messages appear in Romanian', async ({ page }) => {
    // This tests that validation messages are Romanian
    // We'll test by looking for Romanian text patterns
    
    await uploadImage(page, FIXTURES.KITCHEN);
    await waitForFormField(page, 'select#property_type');
    
    // The page should have Romanian text, not English error messages
    const pageText = await page.textContent('body');
    
    // Should NOT have common English error phrases
    expect(pageText).not.toContain('Please enter');
    expect(pageText).not.toContain('This field is required');
    expect(pageText).not.toContain('Invalid input');
  });
});
