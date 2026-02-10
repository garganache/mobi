import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Romanian Localization - Complete Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('complete listing creation flow in Romanian', async ({ page }) => {
    // Step 1: Initial page load - check Romanian text
    await expect(page.locator('text=Pune o poză pentru a începe anunțul')).toBeVisible();
    
    // Step 2: Upload images
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/living_room.jpg');
    await fileInput.setInputFiles(testImage);
    
    // Wait for image to appear
    await expect(page.locator('img[alt*="upload"]')).toBeVisible({ timeout: 5000 });
    
    // Step 3: Trigger analysis (button should be in Romanian)
    const analyzeButton = page.locator('button:has-text("Analizează")');
    await analyzeButton.click();
    
    // Step 4: Wait for analysis results
    await expect(page.locator('text=Prezentare Proprietate')).toBeVisible({ timeout: 30000 });
    
    // Step 5: Verify synthesis display in Romanian
    await expect(page.locator('text=imagini analizate')).toBeVisible();
    await expect(page.locator('text=Camere detectate în imagini')).toBeVisible();
    
    // Check for Romanian room names (at least one should appear)
    const hasRomanianRoom = await page.locator('text=/Dormitor|Bucătărie|Sufragerie|Baie/').isVisible();
    expect(hasRomanianRoom).toBeTruthy();
    
    // Step 6: Check property type dropdown
    await expect(page.locator('label:has-text("Tipul Proprietății")')).toBeVisible();
    
    const propertyTypeSelect = page.locator('select[name="property_type"]');
    await expect(propertyTypeSelect).toBeVisible();
    
    // Open dropdown and verify Romanian options
    await propertyTypeSelect.click();
    await expect(page.locator('option:has-text("Apartament")')).toBeVisible();
    await expect(page.locator('option:has-text("Casă")')).toBeVisible();
    
    // Select property type
    await propertyTypeSelect.selectOption('apartment');
    
    // Verify selected value shows Romanian label
    const selectedText = await propertyTypeSelect.locator('option[selected]').textContent();
    expect(selectedText).toContain('Apartament');
    
    // Step 7: Fill in other fields (labels should be in Romanian)
    await expect(page.locator('label:has-text("Preț")')).toBeVisible();
    await expect(page.locator('label:has-text("Dormitoare")')).toBeVisible();
    
    // Fill some fields
    await page.fill('input[name="price"]', '250000');
    await page.fill('input[name="bedrooms"]', '2');
    
    // Step 8: Click Continue button (Romanian)
    const continueButton = page.locator('button:has-text("Continuă")').first();
    await continueButton.click();
    
    // Step 9: Continue through form until completion
    let step = 0;
    while (step < 5) {
      const continueBtn = page.locator('button:has-text("Continuă")').first();
      if (await continueBtn.isVisible()) {
        await continueBtn.click();
        await page.waitForTimeout(500);
        step++;
      } else {
        break;
      }
    }
    
    // Step 10: Check for completion message in Romanian
    await expect(page.locator('text=Anunț Complet')).toBeVisible({ timeout: 10000 });
    
    // Step 11: Verify Preview & Save button in Romanian
    const previewSaveButton = page.locator('button:has-text("Previzualizare și Salvare")');
    await expect(previewSaveButton).toBeVisible();
    
    // Step 12: Click Preview
    await previewSaveButton.click();
    
    // Step 13: Verify preview page in Romanian
    await expect(page.locator('text=Previzualizare Anunț')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Verificați toate detaliile')).toBeVisible();
    
    // Verify property type shows Romanian in preview
    await expect(page.locator('text=Apartament')).toBeVisible();
    
    // Verify field values are displayed
    await expect(page.locator('text=250')).toBeVisible(); // Price (may be formatted)
    await expect(page.locator('text=2')).toBeVisible(); // Bedrooms
    
    // Step 14: Save listing
    const saveButton = page.locator('button:has-text("Salvează Anunțul")');
    await expect(saveButton).toBeVisible();
    await saveButton.click();
    
    // Step 15: Verify success message in Romanian
    await expect(page.locator('text=Anunț salvat cu succes')).toBeVisible({ timeout: 5000 });
  });

  test('error messages appear in Romanian', async ({ page }) => {
    // Upload image
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/living_room.jpg');
    await fileInput.setInputFiles(testImage);
    
    // Try to preview without property type
    // (Assuming there's a way to trigger this error)
    // This is a placeholder - adjust based on actual error trigger
    
    // Should see Romanian error
    // await expect(page.locator('text=Selectați tipul proprietății')).toBeVisible();
  });

  test('confirmation dialogs in Romanian', async ({ page }) => {
    // Upload and analyze
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/living_room.jpg');
    await fileInput.setInputFiles(testImage);
    
    await page.locator('button:has-text("Analizează")').click();
    await page.waitForTimeout(2000);
    
    // Setup dialog handler
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Sigur doriți să resetați');
      await dialog.accept();
    });
    
    // Click reset button
    const resetButton = page.locator('button:has-text("Resetează formularul")');
    if (await resetButton.isVisible()) {
      await resetButton.click();
    }
  });

  test('room and amenity names in Romanian', async ({ page }) => {
    // Upload image with known rooms/amenities
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/kitchen.jpg');
    await fileInput.setInputFiles(testImage);
    
    await page.locator('button:has-text("Analizează")').click();
    
    // Wait for synthesis
    await expect(page.locator('text=Prezentare Proprietate')).toBeVisible({ timeout: 30000 });
    
    // Check for Romanian room names
    const hasKitchen = await page.locator('text=Bucătărie').isVisible();
    expect(hasKitchen).toBeTruthy();
    
    // Check for Romanian amenities in description
    // Example: "parchet", "blat de granit"
    const descriptionText = await page.locator('.unified-description').textContent();
    // Description should be in Romanian
    expect(descriptionText).toMatch(/Acest|include|Caracteristici/);
  });

  test('property type dropdown maintains English values', async ({ page }) => {
    // This test ensures backend still receives English values
    
    // Upload and analyze
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/living_room.jpg');
    await fileInput.setInputFiles(testImage);
    
    await page.locator('button:has-text("Analizează")').click();
    await page.waitForTimeout(2000);
    
    // Select "Apartament" (Romanian)
    const propertyTypeSelect = page.locator('select[name="property_type"]');
    await propertyTypeSelect.selectOption('apartment'); // English value
    
    // Verify the value attribute is English
    const value = await propertyTypeSelect.inputValue();
    expect(value).toBe('apartment'); // Not "apartament"
    
    // But the displayed text should be Romanian
    const displayText = await propertyTypeSelect.locator('option[selected]').textContent();
    expect(displayText).toContain('Apartament');
  });
});

test.describe('Romanian Localization - Edge Cases', () => {
  test('handles singular vs plural correctly', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Upload single image
    const fileInput = page.locator('input[type="file"]');
    const testImage = path.join(__dirname, '../fixtures/living_room.jpg');
    await fileInput.setInputFiles(testImage);
    
    await page.locator('button:has-text("Analizează")').click();
    
    // Should show "1 imagine analizată" (singular)
    await expect(page.locator('text=1 imagine analizată')).toBeVisible({ timeout: 30000 });
  });

  test('handles multiple images correctly', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Upload multiple images
    const fileInput = page.locator('input[type="file"]');
    const testImages = [
      path.join(__dirname, '../fixtures/living_room.jpg'),
      path.join(__dirname, '../fixtures/bedroom.jpg')
    ];
    await fileInput.setInputFiles(testImages);
    
    await page.locator('button:has-text("Analizează")').click();
    
    // Should show "2 imagini analizate" (plural)
    await expect(page.locator('text=2 imagini analizate')).toBeVisible({ timeout: 30000 });
  });
});