import { test, expect } from '@playwright/test';

test('homepage has correct title', async ({ page }) => {
  await page.goto('/');
  
  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/RaptorFlow/);
});

test('navigation works correctly', async ({ page }) => {
  await page.goto('/');
  
  // Click the get started link.
  await page.getByRole('link', { name: 'Dashboard' }).click();
  
  // Expects the URL to contain dashboard
  await expect(page).toHaveURL(/.*dashboard/);
});
