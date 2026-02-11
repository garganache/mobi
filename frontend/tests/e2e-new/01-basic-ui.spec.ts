import { test, expect } from '@playwright/test';
import { BASE_URL, RO, waitForPageLoad, checkRomanianText } from './helpers';

test.describe('Basic UI - Romanian Production', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
  });

  test('page loads with Romanian interface', async ({ page }) => {
    // Verify main heading
    await expect(page.locator('h1')).toContainText(RO.APP_TITLE);
    
    // Verify get started section
    await expect(page.locator('h2')).toContainText(RO.GET_STARTED);
    
    // Verify file input exists
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached();
  });

  test('displays initial AI message in Romanian', async ({ page }) => {
    // Check for AI guidance message
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toBeVisible();
    
    // Should contain Romanian text
    const text = await aiMessage.textContent();
    expect(text).toContain('Pune o poză');
  });

  test('all key UI elements are present', async ({ page }) => {
    await checkRomanianText(page);
    
    // Check upload zone exists
    const uploadZone = page.locator('.upload-zone, [aria-label*="upload"]').first();
    await expect(uploadZone).toBeVisible();
    
    // Check browse button (in Romanian)
    await expect(page.locator(`text=${RO.BROWSE}`)).toBeVisible();
  });
});
