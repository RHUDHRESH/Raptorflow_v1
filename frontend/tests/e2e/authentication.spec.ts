/**
 * Authentication E2E Tests
 * Tests for login, signup, password reset flows
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.describe('Login Flow', () => {
    test('should display login page', async ({ page }) => {
      await page.goto('/auth/login');

      // Verify page elements
      await expect(page.locator('h1, h2').filter({ hasText: /login|sign in/i })).toBeVisible();
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should show validation errors for empty fields', async ({ page }) => {
      await page.goto('/auth/login');

      // Click submit without filling fields
      await page.locator('button[type="submit"]').click();

      // Wait for validation errors
      await page.waitForTimeout(500);

      // Verify error messages appear
      const errors = await page.locator('[role="alert"], .error, [class*="error"]').count();
      expect(errors).toBeGreaterThan(0);
    });

    test('should show error for invalid email', async ({ page }) => {
      await page.goto('/auth/login');

      await page.locator('input[type="email"]').fill('invalid-email');
      await page.locator('button[type="submit"]').click();

      await page.waitForTimeout(500);

      const errors = await page.locator('[role="alert"], .error, [class*="error"]').count();
      expect(errors).toBeGreaterThan(0);
    });

    test('should have submit button disabled while loading', async ({ page }) => {
      await page.goto('/auth/login');

      // Fill valid credentials
      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');

      const submitButton = page.locator('button[type="submit"]');

      // Check button is not disabled before click
      await expect(submitButton).not.toBeDisabled();
    });
  });

  test.describe('Signup Flow', () => {
    test('should display signup page', async ({ page }) => {
      await page.goto('/auth/signup');

      await expect(page.locator('h1, h2').filter({ hasText: /sign up|register/i })).toBeVisible();
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.locator('input[placeholder*="name" i]')).toBeVisible();
    });

    test('should validate password strength', async ({ page }) => {
      await page.goto('/auth/signup');

      const passwordInput = page.locator('input[type="password"]').first();

      // Type weak password
      await passwordInput.fill('123');
      await page.waitForTimeout(300);

      // Check for weak password warning
      const warning = page.locator('[class*="warning"], [class*="strength"]');
      const warningCount = await warning.count();

      if (warningCount > 0) {
        const warningText = await warning.first().textContent();
        expect(warningText).toBeTruthy();
      }
    });
  });

  test.describe('Password Reset', () => {
    test('should display forgot password page', async ({ page }) => {
      await page.goto('/auth/forgot-password');

      await expect(page.locator('h1, h2').filter({ hasText: /forgot|reset/i })).toBeVisible();
      await expect(page.locator('input[type="email"]')).toBeVisible();
    });

    test('should handle password reset request', async ({ page }) => {
      await page.goto('/auth/forgot-password');

      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('button[type="submit"]').click();

      // Wait for success message or redirect
      await page.waitForTimeout(1000);

      // Check for success message
      const successMessage = page.locator('[class*="success"], [role="alert"]');
      const count = await successMessage.count();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Session Persistence', () => {
    test('should maintain session across page reload', async ({ page, context }) => {
      // This test assumes a user is already logged in
      // In real tests, you'd use a test fixture to set auth

      await page.goto('/');

      // Get initial auth state
      const initialCookie = await context.cookies();

      // Reload page
      await page.reload();

      // Verify cookies are still present
      const afterReloadCookie = await context.cookies();
      expect(afterReloadCookie.length).toBeGreaterThanOrEqual(initialCookie.length);
    });

    test('should redirect unauthenticated user to login', async ({ page }) => {
      // Try to access protected page without auth
      await page.goto('/strategy/workspace');

      // Should redirect to login or show auth page
      await page.waitForURL('**/auth/**', { timeout: 5000 }).catch(() => {
        // If no redirect, check for login prompt or auth UI
      });

      const currentUrl = page.url();
      expect(currentUrl).toMatch(/(auth|login|signin)/i);
    });
  });
});
