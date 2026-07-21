import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  const testEmail = `testuser_${Date.now() + Math.random().toString(36).substring(7)}@example.com`;
  const testPassword = 'Password123!';

  test('should register a new user successfully', async ({ page }) => {
    await page.goto('/login');
    // Switch to register mode
    await page.screenshot({ path: 'debug-login-page.png' });
    await page.getByText(/Don't have an account\? Sign up/i).click();
    
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button:has-text("Sign Up")');

    // Should show success message
    await expect(page.locator('text=Registration successful! Please sign in.')).toBeVisible();
  });

  test('should login successfully and redirect to dashboard', async ({ page }) => {
    const runId = Date.now() + Math.random().toString(36).substring(7);
    await page.goto('/login');
    await page.getByText(/Don't have an account\? Sign up/i).click();
    await page.fill('input[type="email"]', `login_${runId}@example.com`);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button:has-text("Sign Up")');
    await expect(page.locator('text=Registration successful!')).toBeVisible();

    // The form automatically switches back to login? Wait, looking at the code:
    // setIsLogin(true); Error is set to "Registration successful! Please sign in."
    // Let's just fill it again and click Sign In
    await page.fill('input[type="password"]', testPassword); // email is still filled
    await page.click('button:has-text("Sign In")');

    await expect(page).toHaveURL(/.*dashboard/);
    
    // Test Logout
    // Assumes there's a logout button somewhere in the dashboard layout
    // We will just verify dashboard renders.
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'WrongPassword123');
    await page.click('button:has-text("Sign In")');

    await expect(page.locator('.bg-red-500\\/10')).toBeVisible(); // error box
  });
});
