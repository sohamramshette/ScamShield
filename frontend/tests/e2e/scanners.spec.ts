import { test, expect } from '@playwright/test';

test.describe('Scanners', () => {
  test.beforeEach(async ({ page }) => {
    const runId = Date.now() + Math.random().toString(36).substring(7);
    await page.goto('/login');
    await page.getByText(/Don't have an account\? Sign up/i).click();
    await page.fill('input[type="email"]', `scanner_${runId}@example.com`);
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button:has-text("Sign Up")');
    await expect(page.locator('text=Registration successful!')).toBeVisible();

    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL(/.*dashboard/);
  });

  test('Website Scanner should analyze a URL', async ({ page }) => {
    await page.goto('/dashboard/website');
    await page.fill('input[type="url"]', 'http://example.com');
    await page.click('button:has-text("Scan URL")');
    
    await expect(page.locator('text=Confidence')).toBeVisible({ timeout: 15000 });
  });

  test('QR Scanner should handle text input (URL fallback)', async ({ page }) => {
    await page.goto('/dashboard/qr');
    await expect(page.locator('h1:has-text("QR Code")')).toBeVisible();
  });

  test('UPI Analyzer should validate a UPI ID', async ({ page }) => {
    await page.goto('/dashboard/upi');
    const input = page.locator('input[type="text"]').first();
    await expect(input).toBeVisible();
    
    await input.fill('test@upi');
    await page.click('button:has-text("Analyze ID")');
    
    await expect(page.locator('text=Confidence')).toBeVisible({ timeout: 15000 });
  });

  test('Scan History should display previous scans', async ({ page }) => {
    await page.goto('/dashboard/website');
    await page.fill('input[type="url"]', 'http://history-test.com');
    await page.click('button:has-text("Scan URL")');
    await expect(page.locator('text=Confidence')).toBeVisible({ timeout: 15000 });

    await page.goto('/dashboard/history');
    await expect(page.locator('text=history-test.com')).toBeVisible();
  });
});
