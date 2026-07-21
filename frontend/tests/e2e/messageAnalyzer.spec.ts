import { test, expect } from '@playwright/test';

test.describe('Message Analyzer', () => {
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
    
    // Navigate to Message Analyzer
    await page.click('a:has-text("Message Analyzer")');
    await page.waitForURL('/dashboard/message');
  });

  test('should load Message Analyzer page', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Message Analyzer');
    await expect(page.locator('text=Paste Text')).toBeVisible();
    await expect(page.locator('text=Upload Screenshot')).toBeVisible();
  });

  test('should allow pasting text and analyzing', async ({ page }) => {
    // Mock the message analyze API to prevent external LLM calls from slowing down or failing tests
    await page.route('**/api/v1/message/analyze', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'mock-msg-123' }),
      });
    });

    await page.route('**/api/v1/message/mock-msg-123', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'mock-msg-123',
          platform: 'SMS',
          risk_score: 80,
          confidence: 90,
          scam_type: 'Phishing',
          ai_summary: 'Mocked AI summary',
          recommendations: 'Do not click the link.',
          social_engineering_score: 85,
          message_text: 'Your OTP is 123456',
          iocs: []
        }),
      });
    });

    await page.click('text=Paste Text');
    await page.fill('textarea', 'Your OTP is 123456. Do not share this with anyone.');
    
    // Select SMS
    await page.click('label:has-text("SMS")');
    
    await page.click('button:has-text("Analyze Message")');
    
    // Wait for result
    await expect(page.locator('text=AI Threat Summary')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=Scam Type')).toBeVisible();
  });

});
