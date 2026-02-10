import { test, expect } from '@playwright/test';

test('page loads correctly', async ({ page }) => {
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  
  // Basic page load test
  const title = await page.title();
  expect(title).toBe('Mobi UI');
  
  // Check if main heading exists
  const heading = await page.textContent('h1');
  expect(heading).toBe('Mobi Property Listing');
  
  // Check for Get Started section
  const getStarted = await page.textContent('h2');
  expect(getStarted).toBe('Get Started');
  
  console.log('Page loaded successfully');
});