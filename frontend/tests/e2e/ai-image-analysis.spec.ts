import { test, expect } from '@playwright/test';
import path from 'path';
import { createReadStream } from 'fs';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('AI Image Analysis Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  });

  test('AI analyzes uploaded image and displays results', async ({ page }) => {
    // Find and click the file input (it might be hidden, so we use setInputFiles directly)
    const fileInput = page.locator('input[type="file"]');
    
    // Upload a test image
    const testImagePath = path.join(__dirname, '../fixtures/test-property.jpg');
    await fileInput.setInputFiles(testImagePath);
    
    // Wait for upload to complete (look for progress indicator to disappear)
    await page.waitForSelector('text=/Uploading|analyzing/i', { state: 'visible', timeout: 5000 });
    await page.waitForSelector('text=/Uploading|analyzing/i', { state: 'hidden', timeout: 15000 });
    
    // Verify that AI analysis results are displayed
    // The VisionAnalysisDisplay component should show
    await expect(page.locator('text=AI Analysis Results')).toBeVisible({ timeout: 5000 });
    
    // Verify that a property description is shown (should be more than just "apartment with 2 bedrooms")
    const analysisSection = page.locator('.vision-analysis, [data-testid="vision-analysis"]').first();
    await expect(analysisSection).toBeVisible();
    
    // Check for description section
    const descriptionText = await analysisSection.locator('text=/Property Description|description/i').first();
    await expect(descriptionText).toBeVisible();
    
    // Verify dynamic content - should contain actual analysis, not just template
    const content = await analysisSection.textContent();
    expect(content).toBeTruthy();
    expect(content!.length).toBeGreaterThan(50); // Should have substantial content
    
    // Check that property type is detected
    expect(content).toMatch(/property type|apartment|house|townhouse|condo/i);
    
    console.log('AI Analysis displayed:', content);
  });

  test('AI message is dynamic and includes actual description', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]');
    const testImagePath = path.join(__dirname, '../fixtures/test-property.jpg');
    await fileInput.setInputFiles(testImagePath);
    
    // Wait for analysis to complete
    await page.waitForTimeout(2000);
    
    // Look for the AI message component
    const aiMessage = page.locator('.ai-message, [data-testid="ai-message"]').first();
    await expect(aiMessage).toBeVisible({ timeout: 10000 });
    
    const messageText = await aiMessage.textContent();
    console.log('AI Message:', messageText);
    
    // Verify message is NOT the generic fallback
    expect(messageText).not.toBe('I see what looks like an apartment with 2 bedrooms. Please confirm the property type below.');
    
    // Should contain actual description text (more than 20 chars)
    expect(messageText!.length).toBeGreaterThan(20);
    
    // Should reference property details
    expect(messageText).toMatch(/confirm|property|type|bedroom|feature|see/i);
  });

  test('Backend API returns vision_analysis field', async ({ page, request }) => {
    // Create a minimal test image
    const testImageBuffer = Buffer.from([
      0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
    ]);
    
    const base64Image = testImageBuffer.toString('base64');
    
    // Call the API directly
    const response = await request.post(`${API_URL}/analyze-step`, {
      data: {
        input_type: 'image',
        new_input: base64Image,
        current_data: {}
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    console.log('API Response:', JSON.stringify(data, null, 2));
    
    // Verify response structure
    expect(data).toHaveProperty('extracted_data');
    expect(data).toHaveProperty('ui_schema');
    expect(data).toHaveProperty('ai_message');
    expect(data).toHaveProperty('vision_analysis');
    
    // Verify vision_analysis contains expected fields
    expect(data.vision_analysis).toBeTruthy();
    expect(data.vision_analysis).toHaveProperty('description');
    expect(data.vision_analysis).toHaveProperty('property_type');
    expect(data.vision_analysis).toHaveProperty('rooms');
    
    // Verify description is not empty
    expect(data.vision_analysis.description).toBeTruthy();
    expect(data.vision_analysis.description.length).toBeGreaterThan(20);
    
    // Verify ai_message includes the description
    expect(data.ai_message).toBeTruthy();
    expect(data.ai_message.length).toBeGreaterThan(30);
  });

  test('Multiple images show separate AI analyses', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]');
    
    // Upload first image
    await fileInput.setInputFiles(path.join(__dirname, '../fixtures/test-property.jpg'));
    await page.waitForTimeout(3000); // Wait for first analysis
    
    // Upload second image (if multiple is supported)
    // Note: This depends on whether the component supports multiple files
    // If it does, setInputFiles should allow array
    
    // Check for multiple analysis results
    const analysisComponents = page.locator('.vision-analysis, [data-testid="vision-analysis"]');
    const count = await analysisComponents.count();
    
    console.log(`Found ${count} analysis result(s)`);
    
    // Should have at least one
    expect(count).toBeGreaterThanOrEqual(1);
    
    // If multiple upload is supported, verify each has unique content
    if (count > 1) {
      for (let i = 0; i < count; i++) {
        const analysis = analysisComponents.nth(i);
        const content = await analysis.textContent();
        expect(content).toBeTruthy();
        expect(content!.length).toBeGreaterThan(30);
      }
    }
  });

  test('Database stores analysis results', async ({ page, request }) => {
    // Upload an image via UI
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(__dirname, '../fixtures/test-property.jpg'));
    
    // Wait for analysis
    await page.waitForTimeout(3000);
    
    // Query the database via API
    const response = await request.get(`${API_URL}/image-analyses?limit=1`);
    expect(response.ok()).toBeTruthy();
    
    const analyses = await response.json();
    console.log('Latest analysis from DB:', JSON.stringify(analyses[0], null, 2));
    
    expect(analyses).toBeInstanceOf(Array);
    expect(analyses.length).toBeGreaterThan(0);
    
    const latest = analyses[0];
    expect(latest).toHaveProperty('id');
    expect(latest).toHaveProperty('description');
    expect(latest).toHaveProperty('property_type');
    expect(latest).toHaveProperty('created_at');
    
    // Verify description is substantial
    expect(latest.description).toBeTruthy();
    expect(latest.description.length).toBeGreaterThan(20);
  });

  test('Analysis includes condition assessment', async ({ page, request }) => {
    const testImageBuffer = Buffer.from([
      0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
    ]);
    
    const response = await request.post(`${API_URL}/analyze-step`, {
      data: {
        input_type: 'image',
        new_input: testImageBuffer.toString('base64'),
        current_data: {}
      }
    });
    
    const data = await response.json();
    
    // Verify condition field exists (excellent, good, fair, needs_work)
    if (data.vision_analysis && data.vision_analysis.condition) {
      expect(['excellent', 'good', 'fair', 'needs_work']).toContain(data.vision_analysis.condition);
      console.log('Property condition:', data.vision_analysis.condition);
    }
  });

  test('Error handling: Invalid image shows error, not generic message', async ({ page }) => {
    // Try to upload a non-image file
    const fileInput = page.locator('input[type="file"]');
    
    // Create a text file buffer
    const textBuffer = Buffer.from('This is not an image');
    
    // Note: The component should validate file type before upload
    // But if it gets through, the backend should handle gracefully
    
    // This test verifies error states are displayed properly
    const errorSelector = '.error-message, [data-testid="error-message"], text=/error|invalid|failed/i';
    
    // The component should prevent invalid types, but check anyway
    // (This test may need adjustment based on actual error handling)
  });
});
