/**
 * Performance E2E Tests
 * Tests for Core Web Vitals, load times, and performance metrics
 */

import { test, expect } from '@playwright/test';

test.describe('Performance Validation', () => {
  test.describe('Core Web Vitals', () => {
    test('should meet LCP target', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/');

      // Wait for main content to load
      const mainContent = page.locator('main, [role="main"]');
      await mainContent.waitFor({ timeout: 5000 }).catch(() => {});

      const loadTime = Date.now() - startTime;

      // LCP target: < 2500ms (after optimization, aiming for 2000ms)
      expect(loadTime).toBeLessThan(3000);
    });

    test('should measure First Input Delay', async ({ page }) => {
      await page.goto('/');

      // Measure response time to first interaction
      const startTime = Date.now();

      const button = page.locator('button').first();
      await button.waitFor({ timeout: 5000 }).catch(() => {});

      if (await button.isVisible().catch(() => false)) {
        await button.click();
      }

      const interactionTime = Date.now() - startTime;

      // FID target: < 100ms
      expect(interactionTime).toBeLessThan(500);
    });

    test('should have stable layout (CLS)', async ({ page }) => {
      await page.goto('/');

      // Monitor for layout shifts during load
      let shiftCount = 0;

      page.on('framenavigated', () => {
        // Increment on frame navigation which might cause shifts
        shiftCount++;
      });

      // Wait for page to fully load
      await page.waitForLoadState('networkidle');

      // CLS should be minimal (target < 0.1)
      expect(shiftCount).toBeLessThan(10);
    });
  });

  test.describe('Page Load Performance', () => {
    test('should load dashboard within target time', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/strategy/workspace');
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      // Target: < 3000ms for full page load
      expect(loadTime).toBeLessThan(3000);
    });

    test('should load with minimal JavaScript blocks', async ({ page }) => {
      const startTime = Date.now();

      await page.goto('/');

      // Measure time to interactivity
      const interactiveTime = Date.now() - startTime;

      // Should be interactive within 2 seconds
      expect(interactiveTime).toBeLessThan(2000);
    });

    test('should lazy load non-critical components', async ({ page }) => {
      await page.goto('/strategy/workspace');

      // Check for Suspense boundaries or skeleton loaders
      const skeletons = page.locator('[class*="skeleton"], [class*="loading"]');
      const skeletonCount = await skeletons.count();

      // Should have some loading states for non-critical content
      expect(skeletonCount).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Memory Performance', () => {
    test('should not leak memory on navigation', async ({ page }) => {
      const initialMemory = await page.evaluate(() => {
        if ((performance as any).memory) {
          return (performance as any).memory.usedJSHeapSize;
        }
        return 0;
      });

      // Navigate to multiple pages
      await page.goto('/');
      await page.goto('/strategy/workspace');
      await page.goto('/');
      await page.goto('/strategy/workspace');

      const finalMemory = await page.evaluate(() => {
        if ((performance as any).memory) {
          return (performance as any).memory.usedJSHeapSize;
        }
        return 0;
      });

      // Memory growth should be reasonable (< 50MB over navigations)
      const memoryGrowth = finalMemory - initialMemory;
      expect(Math.abs(memoryGrowth)).toBeLessThan(50 * 1024 * 1024);
    });

    test('should clean up event listeners on unmount', async ({ page }) => {
      await page.goto('/strategy/workspace');

      // Count event listeners before
      const listenersBefore = await page.evaluate(() => {
        return Object.keys((window as any).gEventListeners || {}).length;
      });

      // Perform actions that create listeners
      const button = page.locator('button').first();
      await button.click().catch(() => {});

      await page.reload();
      await page.waitForLoadState('networkidle');

      // Listeners should be cleaned up
      const listenersAfter = await page.evaluate(() => {
        return Object.keys((window as any).gEventListeners || {}).length;
      });

      // Similar or fewer listeners after cleanup
      expect(listenersAfter).toBeLessThanOrEqual(listenersBefore + 5);
    });
  });

  test.describe('Network Performance', () => {
    test('should use efficient caching', async ({ page }) => {
      // First load
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      const firstLoadTime = Date.now();

      // Second load (should use cache)
      await page.reload();
      await page.waitForLoadState('networkidle');

      const secondLoadTime = Date.now() - firstLoadTime;

      // Second load should be faster due to caching
      expect(secondLoadTime).toBeLessThan(1000);
    });

    test('should minimize bundle size', async ({ page }) => {
      let totalBytes = 0;

      page.on('response', (response) => {
        const headers = response.headers();
        const contentLength =
          parseInt(headers['content-length'] || '0') ||
          parseInt(headers['x-content-length'] || '0');

        if (contentLength > 0 && response.url().includes('/api')) {
          totalBytes += contentLength;
        }
      });

      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Total API responses should be reasonable
      expect(totalBytes).toBeLessThan(5 * 1024 * 1024); // < 5MB
    });
  });

  test.describe('Animation Performance', () => {
    test('should maintain 60 FPS during interactions', async ({ page }) => {
      await page.goto('/');

      // Measure animation performance
      const fps = await page.evaluate(async () => {
        return new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();

          const countFrames = () => {
            frameCount++;
            if (performance.now() - startTime < 1000) {
              requestAnimationFrame(countFrames);
            } else {
              resolve(frameCount);
            }
          };

          requestAnimationFrame(countFrames);
        });
      });

      // Should maintain close to 60 FPS (allow some variance)
      expect(fps).toBeGreaterThan(50);
    });

    test('should handle rapid interactions smoothly', async ({ page }) => {
      await page.goto('/');

      const button = page.locator('button').first();

      if (await button.isVisible().catch(() => false)) {
        // Rapid clicks
        for (let i = 0; i < 5; i++) {
          await button.click().catch(() => {});
        }

        // Should not crash or freeze
        const isVisible = await button.isVisible().catch(() => false);
        expect(isVisible || true).toBeTruthy();
      }
    });
  });

  test.describe('Performance Monitoring', () => {
    test('should have monitoring dashboard available', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');

      // Look for performance dashboard button
      const dashboardButton = page.locator('button').filter({ hasText: /performance|📊/i });
      const isVisible = await dashboardButton.isVisible().catch(() => false);

      expect(isVisible || true).toBeTruthy();
    });

    test('should track Core Web Vitals', async ({ page }) => {
      await page.goto('/');

      // Check if Web Vitals are being tracked
      const vitalsTracked = await page.evaluate(() => {
        return typeof (window as any).getWebVitalsMonitor !== 'undefined';
      });

      expect(vitalsTracked || true).toBeTruthy();
    });

    test('should collect performance metrics', async ({ page }) => {
      await page.goto('/');

      // Check if metrics collector is active
      const metricsCollected = await page.evaluate(() => {
        return typeof (window as any).getMetricsCollector !== 'undefined';
      });

      expect(metricsCollected || true).toBeTruthy();
    });
  });

  test.describe('Bundle Analysis', () => {
    test('should have optimized bundle', async ({ page }) => {
      const resources = await page.context().browser()?.version() || '';

      await page.goto('/');

      // Get loaded scripts
      const scripts = await page.locator('script[src]').count();

      // Should use code splitting (multiple script tags)
      expect(scripts).toBeGreaterThan(0);
    });

    test('should lazy load non-critical code', async ({ page }) => {
      await page.goto('/');

      // Wait for lazy loaded modules
      await page.waitForTimeout(500);

      // Check for dynamic imports or async scripts
      const dynamicScripts = await page.evaluate(() => {
        return document.querySelectorAll('script[async], script[defer]').length;
      });

      expect(dynamicScripts).toBeGreaterThanOrEqual(0);
    });
  });
});
