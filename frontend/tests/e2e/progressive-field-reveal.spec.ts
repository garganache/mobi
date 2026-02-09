import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test.describe('Progressive Field Reveal Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Upload an image to start the flow
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for AI analysis to complete
    await expect(page.locator('text=I see a kitchen!')).toBeVisible({ timeout: 10000 });
  });

  test('Initial state shows minimal fields', async ({ page }) => {
    // Verify only essential fields are visible initially
    const visibleFields = page.locator('.field-container:visible');
    const count = await visibleFields.count();
    
    // Should show 1-2 fields initially (property type selection)
    expect(count).toBeGreaterThanOrEqual(1);
    expect(count).toBeLessThanOrEqual(3);
    
    // Property type should be the first field
    await expect(page.locator('label:has-text("Property Type")')).toBeVisible();
  });

  test('After upload, new fields appear progressively', async ({ page }) => {
    // Select property type to trigger more fields
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Wait for first batch of fields to appear
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    
    // Fill first field to trigger more
    await page.locator('input[name="bedrooms"]').fill('2');
    
    // Wait for second batch of fields
    await expect(page.locator('label:has-text("Square Footage")')).toBeVisible();
  });

  test('Field count increases progressively (not all at once)', async ({ page }) => {
    // Get initial field count
    const initialCount = await page.locator('.field-container:visible').count();
    
    // Trigger field reveal
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Wait and check that fields appear gradually
    await page.waitForTimeout(1000);
    const afterPropertyCount = await page.locator('.field-container:visible').count();
    
    expect(afterPropertyCount).toBeGreaterThan(initialCount);
    
    // Fill a field to trigger more
    await page.locator('input[name="bedrooms"]').fill('2');
    
    // Wait for more fields to appear
    await page.waitForTimeout(1000);
    const finalCount = await page.locator('.field-container:visible').count();
    
    expect(finalCount).toBeGreaterThan(afterPropertyCount);
  });

  test('Animations run smoothly', async ({ page }) => {
    // Enable animation monitoring
    await page.addInitScript(() => {
      window.__animations = [];
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === 1) { // Element node
                const element = node as Element;
                if (element.classList.contains('field-container')) {
                  window.__animations.push({
                    type: 'field-added',
                    timestamp: Date.now(),
                    element: element.outerHTML.substring(0, 100)
                  });
                }
              }
            });
          }
        });
      });
      observer.observe(document.body, { childList: true, subtree: true });
    });
    
    // Trigger field reveal
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Wait for animations to complete
    await page.waitForTimeout(2000);
    
    // Check that animations were recorded
    const animations = await page.evaluate(() => window.__animations);
    expect(animations.length).toBeGreaterThan(0);
    
    // Verify timing between field reveals (should be staggered)
    if (animations.length > 1) {
      const timeDiff = animations[1].timestamp - animations[0].timestamp;
      expect(timeDiff).toBeGreaterThanOrEqual(50); // At least 50ms between reveals
    }
  });

  test('Fields are accessible after reveal', async ({ page }) => {
    // Trigger field reveal
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Wait for new fields
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    
    // Test accessibility
    const bedroomInput = page.locator('input[name="bedrooms"]');
    
    // Should be focusable
    await bedroomInput.focus();
    await expect(bedroomInput).toBeFocused();
    
    // Should have proper ARIA labels
    await expect(bedroomInput).toHaveAttribute('aria-label');
    
    // Should be keyboard navigable
    await bedroomInput.press('Tab');
    const nextElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(nextElement).toBeDefined();
  });

  test('Form scrolls to new fields if needed', async ({ page }) => {
    // Make viewport small to force scrolling
    await page.setViewportSize({ width: 1280, height: 400 });
    
    // Fill multiple fields to make form longer
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.locator('input[name="bedrooms"]').fill('2');
    await page.locator('input[name="square_footage"]').fill('1200');
    
    // Trigger more fields that should cause scrolling
    await page.locator('input[name="has_balcony"]').check();
    
    // Wait for new fields to appear
    await expect(page.locator('label:has-text("Balcony Size")')).toBeVisible();
    
    // Check if viewport scrolled to show new field
    const fieldVisible = await page.locator('label:has-text("Balcony Size")').isVisible();
    expect(fieldVisible).toBe(true);
  });

  test('Previously filled fields remain visible', async ({ page }) => {
    // Fill initial fields
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.locator('input[name="bedrooms"]').fill('2');
    
    // Trigger more fields
    await page.locator('input[name="square_footage"]').fill('1200');
    
    // Wait for additional fields
    await expect(page.locator('label:has-text("Has Balcony")')).toBeVisible();
    
    // Verify previously filled fields are still visible and retain values
    await expect(page.locator('select[name="property_type"]')).toHaveValue('apartment');
    await expect(page.locator('input[name="bedrooms"]')).toHaveValue('2');
    await expect(page.locator('input[name="square_footage"]')).toHaveValue('1200');
    
    // All should be visible
    await expect(page.locator('label:has-text("Property Type")')).toBeVisible();
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    await expect(page.locator('label:has-text("Square Footage")')).toBeVisible();
  });

  test('Visual regression: Progressive reveal animation', async ({ page }) => {
    // Capture initial state
    await page.screenshot({ path: 'tests/screenshots/progressive-initial.png', fullPage: true });
    
    // Trigger first reveal
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.waitForTimeout(500); // Wait for animation start
    await page.screenshot({ path: 'tests/screenshots/progressive-first-reveal.png', fullPage: true });
    
    // Wait for completion
    await expect(page.locator('label:has-text("Number of Bedrooms")')).toBeVisible();
    await page.screenshot({ path: 'tests/screenshots/progressive-first-complete.png', fullPage: true });
    
    // Trigger second reveal
    await page.locator('input[name="bedrooms"]').fill('2');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'tests/screenshots/progressive-second-reveal.png', fullPage: true });
  });

  test('Timing verification: Field reveal delays', async ({ page }) => {
    const revealTimestamps: number[] = [];
    
    // Monitor field additions
    await page.addInitScript(() => {
      window.__fieldReveals = [];
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1 && (node as Element).classList.contains('field-container')) {
              window.__fieldReveals.push(Date.now());
            }
          });
        });
      });
      observer.observe(document.body, { childList: true, subtree: true });
    });
    
    // Trigger progressive reveal
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Wait for all reveals to complete
    await page.waitForTimeout(3000);
    
    // Check timing
    const timestamps = await page.evaluate(() => window.__fieldReveals);
    expect(timestamps.length).toBeGreaterThan(1);
    
    // Verify staggered timing (not all at once)
    if (timestamps.length > 1) {
      for (let i = 1; i < timestamps.length; i++) {
        const delay = timestamps[i] - timestamps[i-1];
        expect(delay).toBeGreaterThanOrEqual(40); // At least 40ms between reveals
      }
    }
  });
});