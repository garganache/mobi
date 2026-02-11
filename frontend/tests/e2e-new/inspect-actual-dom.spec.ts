import { test } from '@playwright/test';
import { BASE_URL, FIXTURES, waitForPageLoad, uploadImage } from './helpers';

test('inspect actual DOM after upload', async ({ page }) => {
  await page.goto(BASE_URL);
  await waitForPageLoad(page);
  
  console.log('=== BEFORE UPLOAD ===');
  await page.waitForTimeout(2000);
  
  // Upload image
  await uploadImage(page, FIXTURES.KITCHEN);
  
  console.log('=== AFTER UPLOAD (8 seconds) ===');
  
  // Check for various selectors
  const selectors = [
    '.upload-item',
    'img[alt*="kitchen"]',
    'img[src*="blob:"]',
    'img[src*="data:"]',
    'text=kitchen.jpg',
    'text=Imagine 1',
    'text=Imagine',
    'h5:has-text("Imagine")',
    '[role="img"]',
    'article img',
  ];
  
  for (const selector of selectors) {
    const count = await page.locator(selector).count();
    console.log(`${selector}: ${count} elements`);
  }
  
  // Get all img elements
  const allImages = await page.locator('img').count();
  console.log(`\nTotal img elements: ${allImages}`);
  
  // Look for price field
  const priceSelectors = [
    'input#price',
    'input[name="price"]',
    'input[type="number"]',
    'label:has-text("Preț")',
  ];
  
  console.log('\n=== PRICE FIELD SEARCH ===');
  for (const selector of priceSelectors) {
    const count = await page.locator(selector).count();
    const visible = await page.locator(selector).first().isVisible().catch(() => false);
    console.log(`${selector}: ${count} elements, visible: ${visible}`);
  }
  
  // Click Continue
  const continueBtn = page.locator('button:has-text("Continuă")');
  if (await continueBtn.isVisible()) {
    console.log('\n=== CLICKING CONTINUE ===');
    await continueBtn.click();
    await page.waitForTimeout(3000);
    
    console.log('=== AFTER CONTINUE ===');
    for (const selector of priceSelectors) {
      const count = await page.locator(selector).count();
      const visible = await page.locator(selector).first().isVisible().catch(() => false);
      console.log(`${selector}: ${count} elements, visible: ${visible}`);
    }
  }
  
  // Take screenshot
  await page.screenshot({ path: 'test-results/actual-dom-screenshot.png', fullPage: true });
  console.log('\nScreenshot saved to test-results/actual-dom-screenshot.png');
});
