import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test('user can save and see a description', async ({ page }) => {
  await page.goto(BASE_URL);

  const textarea = page.locator('#description');
  const saveButton = page.locator('button', { hasText: 'Save' });

  const text = 'First E2E description';
  await textarea.fill(text);
  await saveButton.click();

  const status = page.locator('[data-testid="status"]');
  await expect(status).toHaveText('Saved successfully');

  // Reload and ensure it still shows
  await page.reload();
  await expect(textarea).toHaveValue(text);
});
