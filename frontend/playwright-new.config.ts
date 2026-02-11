import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e-new',
  timeout: 60000, // 60 seconds per test (production is slower)
  expect: {
    timeout: 15000 // 15 seconds for assertions
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,
  
  reporter: [
    ['html', { outputFolder: 'playwright-report-new' }],
    ['list']
  ],
  
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Production needs longer timeouts
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Don't run local server (we're testing production)
  webServer: undefined,
});
