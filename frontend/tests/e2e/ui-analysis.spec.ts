import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5174';

test.describe('UI Analysis Test', () => {
  test('analyze actual UI after upload', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Check the initial AI message
    const aiMessage = await page.textContent('.ai-message-container');
    console.log('Initial AI message:', aiMessage);
    
    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for analysis
    await page.waitForTimeout(5000);
    
    // Check what text appears
    const newAiMessage = await page.textContent('.ai-message-container');
    console.log('AI message after upload:', newAiMessage);
    
    // Check for synthesis display
    const synthesisText = await page.textContent('.synthesis-container');
    console.log('Synthesis text:', synthesisText);
    
    // Check for form fields
    const formFields = await page.locator('.form-container input, .form-container select').allTextContents();
    console.log('Form field labels:', formFields);
    
    // Check for progress indicator
    const progressText = await page.textContent('.progress-text');
    console.log('Progress text:', progressText);
    
    // Check completion percentage
    const completionPercentage = await page.textContent('.progress-text');
    console.log('Completion percentage:', completionPercentage);
    
    // Check button text
    const buttonText = await page.textContent('.submit-button');
    console.log('Submit button text:', buttonText);
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/ui-analysis.png', fullPage: true });
    
    // Test the actual flow
    expect(newAiMessage).toBeTruthy();
  });
});