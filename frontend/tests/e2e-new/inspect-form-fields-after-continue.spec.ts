import { test } from '@playwright/test';
import { BASE_URL, FIXTURES, waitForPageLoad, uploadImage } from './helpers';

test('inspect form fields after Continue', async ({ page }) => {
  await page.goto(BASE_URL);
  await waitForPageLoad(page);
  
  // Upload image
  await uploadImage(page, FIXTURES.KITCHEN);
  
  // Wait for property type field
  await page.waitForSelector('select#property_type, select[name="property_type"], select', { timeout: 15000 });
  
  // Click Continue
  const continueBtn = page.locator('button:has-text("Continuă")');
  await continueBtn.click();
  await page.waitForTimeout(3000);
  
  console.log('=== ALL INPUT FIELDS ===');
  const allInputs = page.locator('input, select, textarea');
  const count = await allInputs.count();
  console.log(`Total form elements: ${count}`);
  
  for (let i = 0; i < count; i++) {
    const input = allInputs.nth(i);
    const tagName = await input.evaluate(el => el.tagName);
    const type = await input.evaluate(el => el.getAttribute('type'));
    const name = await input.evaluate(el => el.getAttribute('name'));
    const id = await input.evaluate(el => el.id);
    const placeholder = await input.evaluate(el => el.getAttribute('placeholder'));
    const visible = await input.isVisible();
    
    console.log(`[${i}] ${tagName} type="${type}" name="${name}" id="${id}" placeholder="${placeholder}" visible=${visible}`);
  }
  
  // Check labels
  console.log('\n=== ALL LABELS ===');
  const allLabels = page.locator('label');
  const labelCount = await allLabels.count();
  for (let i = 0; i < labelCount; i++) {
    const label = allLabels.nth(i);
    const text = await label.textContent();
    const forAttr = await label.evaluate(el => el.getAttribute('for'));
    console.log(`[${i}] "${text}" for="${forAttr}"`);
  }
  
  await page.screenshot({ path: 'test-results/form-fields-screenshot.png', fullPage: true });
});
