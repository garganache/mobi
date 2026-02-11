/**
 * Test Helpers for Romanian Production Environment
 */
import { Page, expect } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';
export const API_URL = process.env.E2E_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';

// Romanian UI text constants
export const RO = {
  // Page headers
  APP_TITLE: 'Mobi Anunțuri Imobiliare',
  GET_STARTED: 'Începe',
  
  // Buttons
  CONTINUE: 'Continuă',
  ANALYZE: 'Analizează',
  PREVIEW_SAVE: 'Previzualizare și Salvare',
  SAVE_LISTING: 'Salvează Anunțul',
  RESET_FORM: 'Resetează Formularul',
  CREATE_ANOTHER: 'Creează Alt Anunț',
  BROWSE: 'Răsfoiește',
  
  // Messages
  AI_INITIAL: 'Pune o poză pentru a începe anunțul',
  AI_IDENTIFYING: 'Să începem prin a identifica ce tip de proprietate',
  
  // Form labels
  PROPERTY_TYPE: 'Tip Proprietate',
  PRICE: 'Preț',
  BEDROOMS: 'Dormitoare',
  BATHROOMS: 'Băi',
  
  // Property types
  APARTMENT: 'Apartament',
  HOUSE: 'Casă',
  
  // Sections
  PROPERTY_OVERVIEW: 'Prezentare Proprietate',
};

// Test fixtures
export const FIXTURES = {
  KITCHEN: path.join(__dirname, '../fixtures/kitchen.jpg'),
  BEDROOM: path.join(__dirname, '../fixtures/bedroom.jpg'),
  LIVING_ROOM: path.join(__dirname, '../fixtures/living_room.jpg'),
};

// Helper functions
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Let React hydrate
}

export async function uploadImage(page: Page, imagePath: string) {
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(imagePath);
  
  // Wait for upload to complete (production is slow)
  await page.waitForTimeout(6000);
}

export async function uploadMultipleImages(page: Page, imagePaths: string[]) {
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(imagePaths);
  
  // Wait longer for multiple images
  await page.waitForTimeout(8000);
}

export async function waitForFormField(page: Page, selector: string, timeout = 15000) {
  await page.waitForSelector(selector, { 
    state: 'visible', 
    timeout 
  });
}

export async function clickContinue(page: Page) {
  const continueBtn = page.locator(`button:has-text("${RO.CONTINUE}")`);
  await continueBtn.click();
  await page.waitForTimeout(1500);
}

export async function fillPropertyForm(page: Page, data: {
  propertyType?: string;
  bedrooms?: string;
  bathrooms?: string;
  squareFeet?: string;
}) {
  if (data.propertyType) {
    await page.locator('select#property_type').selectOption(data.propertyType);
    await page.waitForTimeout(500);
  }
  
  // Note: bedrooms, bathrooms, squareFeet appear after clicking Continue
  if (data.bedrooms) {
    const bedroomsField = page.locator('input#bedrooms');
    await bedroomsField.waitFor({ state: 'visible', timeout: 20000 });
    await bedroomsField.fill(data.bedrooms);
    await page.waitForTimeout(500);
  }
  
  if (data.bathrooms) {
    const bathroomsField = page.locator('input#bathrooms');
    await bathroomsField.waitFor({ state: 'visible', timeout: 20000 });
    await bathroomsField.fill(data.bathrooms);
    await page.waitForTimeout(500);
  }
  
  if (data.squareFeet) {
    const squareFeetField = page.locator('input#square_feet');
    await squareFeetField.waitFor({ state: 'visible', timeout: 20000 });
    await squareFeetField.fill(data.squareFeet);
    await page.waitForTimeout(500);
  }
}

export async function verifyUploadedImages(page: Page, expectedCount: number) {
  // In production, uploaded images appear as "Imagine 1", "Imagine 2", etc.
  await page.waitForTimeout(3000); // Give React time to render
  
  // Check for "Prezentare Proprietate" section which confirms upload
  await expect(page.locator('h3:has-text("Prezentare Proprietate")')).toBeVisible({ timeout: 20000 });
  
  // Check for image count text (e.g., "1 imagine analizată", "3 imagini analizate")
  const imageCountText = page.locator('text=/\\d+ imagin/i');
  await expect(imageCountText).toBeVisible({ timeout: 10000 });
}

export async function checkRomanianText(page: Page) {
  // Verify key Romanian text is present
  await expect(page.locator(`h1:has-text("${RO.APP_TITLE}")`)).toBeVisible();
  await expect(page.locator(`h2:has-text("${RO.GET_STARTED}")`)).toBeVisible();
}
