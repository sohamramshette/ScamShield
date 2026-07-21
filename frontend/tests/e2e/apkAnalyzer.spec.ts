import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('APK Analyzer', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the auth login API response
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ access_token: 'fake-token', token_type: 'bearer' }),
      });
    });

    // Mock the user profile API response
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 1, email: 'test@scamshield.ai', is_active: true }),
      });
    });

    // Navigate to the dashboard
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@scamshield.ai');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('/dashboard');
    
    // Navigate to APK Analyzer
    await page.click('a:has-text("APK Analyzer")');
    await page.waitForURL('/dashboard/apk');
  });

  test('should load APK Analyzer page', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('APK Malware Analyzer');
    await expect(page.locator('text=Upload APK File')).toBeVisible();
  });
  
  test('should allow uploading an APK and analyze', async ({ page }) => {
    // Create a mock route for analyze so we don't have to upload a real large file during frontend testing
    await page.route('**/api/v1/apk/analyze', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'mock-apk-scan-123', status: 'completed' }),
      });
    });

    await page.route('**/api/v1/apk/mock-apk-scan-123', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'mock-apk-scan-123',
          filename: 'test.apk',
          package_name: 'com.test.app',
          version: '1.0',
          risk_score: 85,
          confidence: 90,
          malware_family: 'Android_RAT',
          ai_summary: 'Mock Malicious APK',
          recommendations: 'Do not install',
          permissions: [{permission: 'android.permission.CAMERA', dangerous: true, severity: 'High'}],
          components: [],
          certificates: [],
          iocs: []
        }),
      });
    });
    
    // We upload a dummy file via input[type="file"]
    // We can't easily upload a real file if it doesn't exist, so we use playwright's setInputFiles
    // We'll create a dummy buffer
    await page.setInputFiles('input[type="file"]', {
        name: 'test.apk',
        mimeType: 'application/vnd.android.package-archive',
        buffer: Buffer.from('mock apk content')
    });
    
    await page.click('button:has-text("Analyze APK")');
    
    // Wait for result
    await expect(page.locator('text=AI Threat Summary')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=CRITICAL RISK')).toBeVisible();
  });
});
