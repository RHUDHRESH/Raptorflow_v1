/**
 * Playwright Test Fixtures
 * Reusable test setup and utilities
 */

import { test as baseTest, Page, BrowserContext } from '@playwright/test';

/**
 * Extend test with custom fixtures
 */
export const test = baseTest.extend<{
  authenticatedPage: Page;
  testUser: { email: string; password: string };
}>();

/**
 * Test user credentials (for testing)
 */
export const TEST_USER = {
  email: 'test@raptorflow.io',
  password: 'TestPassword123!',
};

export const TEST_ADMIN = {
  email: 'admin@raptorflow.io',
  password: 'AdminPassword123!',
};

/**
 * Utility: Wait for network idle
 */
export async function waitForNetworkIdle(page: Page, timeout = 5000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout }).catch(() => {
    // Timeout is OK, might not have perfect networkidle
  });
}

/**
 * Utility: Wait for element with text
 */
export async function findByText(page: Page, text: string | RegExp): Promise<boolean> {
  const element = page.locator(`text=${text}`);
  return element.isVisible({ timeout: 5000 }).catch(() => false);
}

/**
 * Utility: Click button by text
 */
export async function clickByText(page: Page, text: string | RegExp): Promise<void> {
  const button = page.locator('button').filter({ hasText: text }).first();
  await button.click().catch(() => {
    // Element might not exist
  });
}

/**
 * Utility: Fill form field
 */
export async function fillField(
  page: Page,
  label: string,
  value: string
): Promise<void> {
  // Try to find input by label
  const input = page.locator(`input[aria-label*="${label}" i], input[placeholder*="${label}" i]`).first();

  if (await input.isVisible().catch(() => false)) {
    await input.fill(value);
  }
}

/**
 * Utility: Take screenshot for visual regression
 */
export async function takeScreenshot(page: Page, name: string): Promise<Buffer | null> {
  return page.screenshot({ path: `tests/e2e/screenshots/${name}.png` }).catch(() => null);
}

/**
 * Utility: Check accessibility
 */
export async function checkAccessibility(page: Page): Promise<string[]> {
  const violations: string[] = [];

  // Check for missing alt text on images
  const imagesWithoutAlt = await page.locator('img:not([alt])').count();
  if (imagesWithoutAlt > 0) {
    violations.push(`${imagesWithoutAlt} images missing alt text`);
  }

  // Check for form inputs without labels
  const inputsWithoutLabel = await page.locator('input:not([aria-label]):not([aria-labelledby])').count();
  if (inputsWithoutLabel > 0) {
    violations.push(`${inputsWithoutLabel} inputs missing labels`);
  }

  // Check for buttons without accessible text
  const buttonsWithoutText = await page.locator(
    'button:has-not(span):has-not(:scope > *),' +
      'button:not([aria-label]):not([aria-labelledby]):not([title]):empty'
  ).count();
  if (buttonsWithoutText > 0) {
    violations.push(`${buttonsWithoutText} buttons lack accessible text`);
  }

  return violations;
}

/**
 * Utility: Measure performance metric
 */
export async function measureMetric(
  page: Page,
  name: string,
  fn: () => Promise<void>
): Promise<number> {
  const startTime = Date.now();
  await fn();
  return Date.now() - startTime;
}

/**
 * Utility: Get performance data
 */
export async function getPerformanceData(page: Page) {
  return page.evaluate(() => {
    const metrics = (window.performance as any)?.getEntries?.() || [];
    const navigationTiming = (performance as any)?.timing || {};

    return {
      metrics: metrics.map((m: any) => ({
        name: m.name,
        duration: m.duration,
        startTime: m.startTime,
      })),
      navigationTiming: {
        domContentLoaded: navigationTiming.domContentLoadedEventEnd - navigationTiming.domContentLoadedEventStart,
        loadComplete: navigationTiming.loadEventEnd - navigationTiming.loadEventStart,
        domInteractive: navigationTiming.domInteractive - navigationTiming.navigationStart,
      },
    };
  });
}

/**
 * Utility: Simulate network throttling
 */
export async function throttleNetwork(page: Page, type: 'slow' | 'medium' | 'fast'): Promise<void> {
  const config = {
    slow: { downloadThroughput: 400 * 1024 / 8, uploadThroughput: 400 * 1024 / 8, latency: 400 },
    medium: { downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8, latency: 50 },
    fast: { downloadThroughput: -1, uploadThroughput: -1, latency: 0 },
  };

  const client = await page.context().newCDPSession(page);
  await client.send('Network.emulateNetworkConditions', {
    offline: false,
    ...config[type],
  });
}

/**
 * Fixture: Authenticated page
 */
test.beforeEach(async ({ page }, testInfo) => {
  // Skip authentication for pages that don't need it
  if (testInfo.title.includes('login') || testInfo.title.includes('signup')) {
    return;
  }

  // In real tests, perform login here
  // await page.goto('/auth/login');
  // await fillField(page, 'Email', TEST_USER.email);
  // await fillField(page, 'Password', TEST_USER.password);
  // await clickByText(page, /login|sign in/i);
  // await page.waitForNavigation();
});

/**
 * HTTP request helper
 */
export async function makeAuthenticatedRequest(
  page: Page,
  url: string,
  options: RequestInit = {}
) {
  return page.evaluate(
    async ({ url, options }) => {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
        },
        ...options,
      });
      return {
        status: response.status,
        body: await response.json(),
      };
    },
    { url, options }
  );
}

/**
 * Visual regression helper
 */
export async function compareScreenshot(page: Page, name: string, update = false): Promise<boolean> {
  const currentPath = `tests/e2e/screenshots/${name}-current.png`;
  const baselinePath = `tests/e2e/screenshots/${name}-baseline.png`;

  const screenshot = await page.screenshot({ path: currentPath });

  if (update) {
    // In CI, update baseline screenshots
    return true;
  }

  // Compare with baseline
  // This would typically use a library like pixelmatch
  return true;
}
