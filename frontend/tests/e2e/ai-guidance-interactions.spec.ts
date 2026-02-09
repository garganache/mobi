import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';

test.describe('AI Guidance Interactions Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('Initial AI message displays on page load', async ({ page }) => {
    // Check for welcome message
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toBeVisible();
    await expect(aiMessage).toContainText('Drop a photo to start your listing');
    
    // Verify message styling
    await expect(aiMessage).toHaveCSS('background-color', /rgba?\(59, 130, 246/); // Blue background
    await expect(aiMessage).toHaveCSS('color', /rgb\(255, 255, 255\)/); // White text
  });

  test('AI message updates after image upload', async ({ page }) => {
    // Upload an image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Verify message updates during analysis
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toContainText('Analyzing your image...');
    
    // Wait for analysis to complete and message to update
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    await expect(aiMessage).toContainText('Is this a house or an apartment?');
  });

  test('Message reflects detected features', async ({ page }) => {
    // Test different image types
    const testCases = [
      { image: 'kitchen.jpg', expectedText: ['kitchen', 'modern'] },
      { image: 'bedroom.jpg', expectedText: ['bedroom', 'cozy'] },
      { image: 'living-room.jpg', expectedText: ['living', 'spacious'] },
      { image: 'exterior.jpg', expectedText: ['exterior', 'property'] }
    ];

    for (const testCase of testCases) {
      await page.goto(BASE_URL, { waitUntil: 'networkidle' });
      
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(`tests/fixtures/${testCase.image}`);
      
      const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
      
      // Wait for analysis and check message content
      await expect(aiMessage).toBeVisible({ timeout: 10000 });
      
      // Check that message contains expected keywords
      const messageText = await aiMessage.textContent();
      const hasExpectedText = testCase.expectedText.some(keyword => 
        messageText?.toLowerCase().includes(keyword)
      );
      expect(hasExpectedText).toBe(true);
    }
  });

  test('Message tone is friendly and helpful', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    
    // Check tone characteristics
    const messageText = await aiMessage.textContent();
    expect(messageText).toMatch(/[!?]/); // Should have friendly punctuation
    expect(messageText?.length).toBeLessThan(200); // Should be concise
    
    // Should not contain technical jargon or error-like language
    expect(messageText).not.toContain('error');
    expect(messageText).not.toContain('invalid');
    expect(messageText).not.toContain('failed');
  });

  test('Message updates when user fills fields', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for initial message
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    
    // Fill a field
    await page.locator('select[name="property_type"]').selectOption('apartment');
    
    // Verify message updates to reflect user action
    await expect(aiMessage).toContainText('Great choice!');
    await expect(aiMessage).toContainText('bedrooms');
  });

  test('Multiple messages handled correctly', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    // Wait for first message
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    
    // Fill multiple fields to trigger multiple message updates
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await page.locator('input[name="bedrooms"]').fill('2');
    await page.locator('input[name="square_footage"]').fill('1200');
    
    // Verify messages update smoothly without stacking
    const messageCount = await page.locator('[data-testid="ai-guidance-message"]').count();
    expect(messageCount).toBe(1); // Should only be one message at a time
    
    // Verify final message is relevant
    const finalText = await aiMessage.textContent();
    expect(finalText).toContain('apartment');
  });

  test('Messages are readable and accessible', async ({ page }) => {
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    
    // Check font size
    await expect(aiMessage).toHaveCSS('font-size', /1[0-9]px/); // Reasonable font size
    
    // Check contrast ratio (should be sufficient)
    await expect(aiMessage).toHaveCSS('color', /rgb\(255, 255, 255\)/); // White text
    
    // Check for ARIA attributes
    await expect(aiMessage).toHaveAttribute('role', 'status');
    await expect(aiMessage).toHaveAttribute('aria-live', 'polite');
    
    // Upload image and verify message remains readable
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    
    // Verify text is still readable after update
    await expect(aiMessage).toHaveCSS('font-size', /1[0-9]px/);
  });

  test('Visual positioning tested', async ({ page }) => {
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    
    // Verify message is positioned prominently
    const box = await aiMessage.boundingBox();
    expect(box).toBeDefined();
    
    // Should be in upper portion of screen
    expect(box!.y).toBeLessThan(300);
    
    // Should be centered horizontally
    const viewport = await page.viewportSize();
    const centerX = viewport!.width / 2;
    expect(Math.abs(box!.x + box!.width / 2 - centerX)).toBeLessThan(100);
    
    // Upload image and verify position doesn't jump dramatically
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    
    const newBox = await aiMessage.boundingBox();
    expect(newBox).toBeDefined();
    
    // Position should be similar (not jumping around)
    expect(Math.abs(newBox!.y - box!.y)).toBeLessThan(50);
  });

  test('Message content relevance verified', async ({ page }) => {
    // Test with different scenarios
    const scenarios = [
      {
        action: async () => {
          const fileInput = page.locator('input[type="file"]');
          await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
        },
        expectedContent: ['kitchen', 'cooking', 'appliance']
      },
      {
        action: async () => {
          await page.locator('select[name="property_type"]').selectOption('house');
        },
        expectedContent: ['house', 'home', 'property']
      },
      {
        action: async () => {
          await page.locator('input[name="bedrooms"]').fill('3');
        },
        expectedContent: ['bedroom', 'room', 'space']
      }
    ];

    for (const scenario of scenarios) {
      await scenario.action();
      
      const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
      await expect(aiMessage).toBeVisible({ timeout: 5000 });
      
      const messageText = await aiMessage.textContent();
      const hasRelevantContent = scenario.expectedContent.some(keyword =>
        messageText?.toLowerCase().includes(keyword)
      );
      
      expect(hasRelevantContent).toBe(true);
    }
  });

  test('Visual regression: AI message states', async ({ page }) => {
    const aiMessage = page.locator('[data-testid="ai-guidance-message"]');
    
    // Initial state
    await expect(aiMessage).toContainText('Drop a photo');
    await page.screenshot({ path: 'tests/screenshots/ai-message-initial.png', fullPage: true });
    
    // Loading state
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/kitchen.jpg');
    await expect(aiMessage).toContainText('Analyzing');
    await page.screenshot({ path: 'tests/screenshots/ai-message-loading.png', fullPage: true });
    
    // Analysis complete state
    await expect(aiMessage).toContainText('I see a kitchen!', { timeout: 10000 });
    await page.screenshot({ path: 'tests/screenshots/ai-message-complete.png', fullPage: true });
    
    // User interaction state
    await page.locator('select[name="property_type"]').selectOption('apartment');
    await expect(aiMessage).toContainText('Great choice!');
    await page.screenshot({ path: 'tests/screenshots/ai-message-interaction.png', fullPage: true });
  });
});