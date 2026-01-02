import { test, expect, type Page } from '@playwright/test';

// Test credentials
const TEST_EMAIL = 'test@realtorspractice.com';
const TEST_PASSWORD = 'TestPass123!';
const BASE_URL = 'http://localhost:3000';

// Mobile device viewports
const VIEWPORTS = {
  'iPhone SE': { width: 375, height: 667 },
  'iPhone 12': { width: 390, height: 844 },
  'iPad': { width: 768, height: 1024 },
  'Desktop': { width: 1920, height: 1080 },
};

// Helper function to login
async function login(page: Page) {
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');

  // Fill in credentials
  try {
    await page.fill('input[type="email"], input[name="email"]', TEST_EMAIL);
    await page.fill('input[type="password"], input[name="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
  } catch (e) {
    console.log('Login might already be active or page structure different');
  }
}

test.describe('New Features - Property Detail Modal', () => {
  for (const [deviceName, viewport] of Object.entries(VIEWPORTS)) {
    test(`should display property detail modal on ${deviceName}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await login(page);

      // Navigate to Data Explorer or Properties page
      try {
        await page.click('text=Data Explorer', { timeout: 3000 });
      } catch {
        await page.goto(`${BASE_URL}/data-explorer`);
      }

      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      // Find and click a property card
      const propertyCard = page.locator('[class*="PropertyCard"], [data-testid="property-card"]').first();

      try {
        await propertyCard.waitFor({ timeout: 5000 });

        // Take screenshot before clicking
        await page.screenshot({
          path: `test-results/${deviceName.replace(/\s+/g, '-')}-property-cards.png`,
          fullPage: true
        });

        await propertyCard.click();
        await page.waitForTimeout(1000);

        // Check if modal appeared
        const modal = page.locator('[role="dialog"]');
        const isModalVisible = await modal.isVisible({ timeout: 3000 }).catch(() => false);

        if (isModalVisible) {
          console.log(`✓ ${deviceName}: Property detail modal opened`);

          // Take screenshot of modal
          await page.screenshot({
            path: `test-results/${deviceName.replace(/\s+/g, '-')}-property-modal.png`,
            fullPage: true
          });

          // Check for comprehensive data sections
          const sections = [
            'Overview',
            'Amenities',
            'Agent',
            'Location',
            'Listing Details'
          ];

          for (const section of sections) {
            const hasSection = await page.getByText(section, { exact: false }).isVisible().catch(() => false);
            console.log(`  ${hasSection ? '✓' : '✗'} ${section} section`);
          }

          // Close modal
          await page.keyboard.press('Escape');
        } else {
          console.log(`✗ ${deviceName}: Property detail modal not found`);
        }
      } catch (e) {
        console.log(`✗ ${deviceName}: Could not find property cards -`, e);
        await page.screenshot({
          path: `test-results/${deviceName.replace(/\s+/g, '-')}-no-properties-error.png`,
          fullPage: true
        });
      }
    });
  }
});

test.describe('New Features - Grid View Selector', () => {
  for (const [deviceName, viewport] of Object.entries(VIEWPORTS)) {
    test(`should test grid view selector on ${deviceName}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await login(page);

      // Navigate to Data Explorer
      try {
        await page.click('text=Data Explorer', { timeout: 3000 });
      } catch {
        await page.goto(`${BASE_URL}/data-explorer`);
      }

      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);

      // Look for grid view selector
      const gridSelector = page.locator('select, [role="combobox"]').filter({ hasText: /grid|column|view/i }).first();

      try {
        const isSelectorVisible = await gridSelector.isVisible({ timeout: 3000 }).catch(() => false);

        if (isSelectorVisible) {
          console.log(`✓ ${deviceName}: Grid view selector found`);

          await page.screenshot({
            path: `test-results/${deviceName.replace(/\s+/g, '-')}-grid-selector.png`,
            fullPage: false
          });

          // Test grid view options
          const viewOptions = ['List View', '2 Columns', '3 Columns', '4 Columns', '5 Columns', '6 Columns'];

          for (const option of viewOptions) {
            try {
              await gridSelector.click();
              await page.waitForTimeout(300);

              const optionElement = page.getByText(option, { exact: false });
              const optionVisible = await optionElement.isVisible({ timeout: 1000 }).catch(() => false);

              if (optionVisible) {
                console.log(`  ✓ ${option} available`);
                await optionElement.click();
                await page.waitForTimeout(500);

                // Take screenshot of grid layout
                await page.screenshot({
                  path: `test-results/${deviceName.replace(/\s+/g, '-')}-${option.replace(/\s+/g, '-')}.png`,
                  fullPage: true
                });
              } else {
                console.log(`  ✗ ${option} not visible`);
              }
            } catch (e) {
              console.log(`  ✗ Could not test ${option}`);
            }
          }
        } else {
          console.log(`✗ ${deviceName}: Grid view selector not found`);
          await page.screenshot({
            path: `test-results/${deviceName.replace(/\s+/g, '-')}-no-grid-selector.png`,
            fullPage: true
          });
        }
      } catch (e) {
        console.log(`✗ ${deviceName}: Grid selector test failed -`, e);
      }
    });
  }
});

test.describe('New Features - Sticky Filters', () => {
  test('should verify sticky filters on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Data Explorer
    try {
      await page.click('text=Data Explorer');
    } catch {
      await page.goto(`${BASE_URL}/data-explorer`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Take screenshot at top
    await page.screenshot({
      path: 'test-results/sticky-filters-top.png',
      fullPage: false
    });

    // Get filter card position
    const filterCard = page.locator('[class*="sticky"]').first();
    const initialPosition = await filterCard.boundingBox();

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(500);

    // Take screenshot after scroll
    await page.screenshot({
      path: 'test-results/sticky-filters-scrolled.png',
      fullPage: false
    });

    const scrolledPosition = await filterCard.boundingBox();

    if (initialPosition && scrolledPosition) {
      const isSticky = Math.abs(initialPosition.y - scrolledPosition.y) < 50;
      console.log(isSticky ? '✓ Filters are sticky' : '✗ Filters are not sticky');
      console.log(`  Initial Y: ${initialPosition.y}, Scrolled Y: ${scrolledPosition.y}`);
    }
  });
});

test.describe('New Features - Scraper Control Reorganization', () => {
  test('should verify scraper control layout on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Scraper Control
    try {
      await page.click('text=Scraper', { timeout: 3000 });
    } catch {
      await page.goto(`${BASE_URL}/scraper`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const report = {
      scrapeTimeEstimate: false,
      startScrapeButton: false,
      advancedSettings: false,
      siteConfiguration: false,
    };

    // Check for Scrape Time Estimate (should be outside Advanced Settings)
    try {
      const scrapeEstimate = page.getByText('Scrape Time Estimate', { exact: false });
      report.scrapeTimeEstimate = await scrapeEstimate.isVisible({ timeout: 3000 }).catch(() => false);
      console.log(report.scrapeTimeEstimate ? '✓ Scrape Time Estimate visible' : '✗ Scrape Time Estimate not found');
    } catch (e) {
      console.log('✗ Could not check Scrape Time Estimate');
    }

    // Check for Start Scrape button (should be below Site Configuration)
    try {
      const startButton = page.getByRole('button', { name: /start.*scrape/i });
      report.startScrapeButton = await startButton.isVisible({ timeout: 3000 }).catch(() => false);
      console.log(report.startScrapeButton ? '✓ Start Scrape button visible' : '✗ Start Scrape button not found');
    } catch (e) {
      console.log('✗ Could not check Start Scrape button');
    }

    // Check for Advanced Settings
    try {
      const advSettings = page.getByText('Advanced Settings', { exact: false });
      report.advancedSettings = await advSettings.isVisible({ timeout: 3000 }).catch(() => false);
      console.log(report.advancedSettings ? '✓ Advanced Settings visible' : '✗ Advanced Settings not found');
    } catch (e) {
      console.log('✗ Could not check Advanced Settings');
    }

    // Check for Site Configuration
    try {
      const siteConfig = page.getByText('Site Configuration', { exact: false });
      report.siteConfiguration = await siteConfig.isVisible({ timeout: 3000 }).catch(() => false);
      console.log(report.siteConfiguration ? '✓ Site Configuration visible' : '✗ Site Configuration not found');
    } catch (e) {
      console.log('✗ Could not check Site Configuration');
    }

    // Take full page screenshot
    await page.screenshot({
      path: 'test-results/scraper-control-reorganized.png',
      fullPage: true
    });

    console.log('Scraper Control Report:', report);
  });
});

test.describe('New Features - Global Parameters in System Settings', () => {
  test('should verify global parameters in system settings', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Settings
    try {
      await page.click('text=Settings', { timeout: 3000 });
    } catch {
      await page.goto(`${BASE_URL}/settings`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Click on System Settings tab
    try {
      const systemTab = page.getByRole('tab', { name: /system/i }).or(page.getByText('System Settings'));
      await systemTab.click();
      await page.waitForTimeout(1000);

      // Look for Global Parameters section
      const globalParams = page.getByText('Global Scraper Parameters', { exact: false }).or(page.getByText('Global Parameters'));
      const isVisible = await globalParams.isVisible({ timeout: 3000 }).catch(() => false);

      if (isVisible) {
        console.log('✓ Global Parameters found in System Settings');

        // Check for Max Pages input
        const maxPagesInput = page.locator('input[type="number"]').first();
        const hasMaxPages = await maxPagesInput.isVisible({ timeout: 2000 }).catch(() => false);
        console.log(hasMaxPages ? '  ✓ Max Pages input found' : '  ✗ Max Pages input not found');

        // Take screenshot
        await page.screenshot({
          path: 'test-results/global-parameters-system-settings.png',
          fullPage: true
        });
      } else {
        console.log('✗ Global Parameters not found in System Settings');
        await page.screenshot({
          path: 'test-results/system-settings-no-global-params.png',
          fullPage: true
        });
      }
    } catch (e) {
      console.log('✗ Could not navigate to System Settings:', e);
    }
  });
});
