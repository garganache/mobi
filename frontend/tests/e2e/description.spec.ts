import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

// CI can be a bit slow to start the preview server; give this test more time
// and wait explicitly for the textarea to appear before interacting.
test('user can save and see a description', async ({ page }) => {
  test.setTimeout(60000);

  page.on('console', (msg) => {
    console.log('browser console:', msg.type(), msg.text());
  });
  page.on('pageerror', (err) => {
    console.log('pageerror:', err.message);
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });

  // Debug output for CI: see what the page actually looks like
  console.log('E2E: loaded URL', BASE_URL);
  console.log('E2E: page content snippet:', (await page.content()).slice(0, 500));

  const textarea = page.locator('#description');
  const saveButton = page.locator('button', { hasText: 'Save' });

  await textarea.waitFor({ state: 'visible', timeout: 30000 });

  const text = 'First E2E description';
  await textarea.fill(text);
  await saveButton.click();

  const status = page.locator('[data-testid="status"]');
  await expect(status).toHaveText('Saved successfully');

  // Reload and ensure it still shows
  await page.reload();
  await expect(textarea).toHaveValue(text);
});
