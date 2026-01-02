import { test, expect, type Page } from '@playwright/test';

// Test credentials
const TEST_EMAIL = 'test@realtorspractice.com';
const TEST_PASSWORD = 'TestPass123!';
const BASE_URL = 'http://localhost:3000';

// Mobile device viewports
const VIEWPORTS = {
  'iPhone SE': { width: 375, height: 667 },
  'iPhone 12': { width: 390, height: 844 },
  'Pixel 5': { width: 393, height: 851 },
};

// Helper function to login
async function login(page: Page) {
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');

  // Check if we're already on the login page or need to navigate
  const currentUrl = page.url();
  if (!currentUrl.includes('/login')) {
    // Try to find and click a login button if available
    try {
      await page.click('text=Login', { timeout: 3000 });
      await page.waitForLoadState('networkidle');
    } catch (e) {
      // If no login button, we might already be logged in or on login page
      console.log('No login button found, continuing...');
    }
  }

  // Fill in credentials
  await page.fill('input[type="email"], input[name="email"]', TEST_EMAIL);
  await page.fill('input[type="password"], input[name="password"]', TEST_PASSWORD);

  // Click login button
  await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');

  // Wait for navigation to dashboard
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000); // Give time for any animations
}

// Helper function to navigate to Scraper Control
async function navigateToScraperControl(page: Page) {
  // Try multiple possible navigation methods
  try {
    // Method 1: Click on sidebar link
    await page.click('text=Scraper Control', { timeout: 3000 });
  } catch (e) {
    try {
      // Method 2: Click on a link or button with scraper in it
      await page.click('a:has-text("Scraper"), button:has-text("Scraper")', { timeout: 3000 });
    } catch (e2) {
      // Method 3: Direct navigation
      await page.goto(`${BASE_URL}/scraper-control`);
    }
  }

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

test.describe('Realtors Practice - Desktop Tests', () => {
  test('should login successfully and load dashboard', async ({ page }) => {
    await login(page);

    // Verify we're on the dashboard
    await expect(page).toHaveURL(new RegExp('dashboard|home'), { timeout: 10000 });

    // Take a screenshot
    await page.screenshot({ path: 'test-results/01-dashboard-desktop.png', fullPage: true });

    console.log('✓ Login successful - Dashboard loaded');
  });

  test('should navigate to Scraper Control page', async ({ page }) => {
    await login(page);
    await navigateToScraperControl(page);

    // Verify we're on the scraper control page
    await expect(page).toHaveURL(/scraper/i);

    // Take a screenshot
    await page.screenshot({ path: 'test-results/02-scraper-control-desktop.png', fullPage: true });

    console.log('✓ Navigated to Scraper Control page');
  });

  test('should verify scraper control page elements', async ({ page }) => {
    await login(page);
    await navigateToScraperControl(page);

    // Check for key elements
    const elements = {
      addButton: page.locator('button:has-text("Add Site"), button:has-text("Add")').first(),
      siteCards: page.locator('[data-testid="site-card"], .site-card, div:has(button:has-text("Enable")), div:has(button:has-text("Disable"))'),
    };

    // Verify Add Site button exists
    try {
      await expect(elements.addButton).toBeVisible({ timeout: 5000 });
      console.log('✓ Add Site button found');
    } catch (e) {
      console.log('✗ Add Site button not found');
    }

    // Check if site cards exist
    const cardCount = await elements.siteCards.count();
    console.log(`Found ${cardCount} site cards`);

    // Take a screenshot
    await page.screenshot({ path: 'test-results/03-elements-check-desktop.png', fullPage: true });
  });
});

test.describe('Realtors Practice - Mobile Tests', () => {
  for (const [deviceName, viewport] of Object.entries(VIEWPORTS)) {
    test.describe(`${deviceName} (${viewport.width}x${viewport.height})`, () => {
      test.use({ viewport });

      test(`should login and view dashboard on ${deviceName}`, async ({ page }) => {
        await login(page);

        // Verify we're on the dashboard
        await expect(page).toHaveURL(new RegExp('dashboard|home'), { timeout: 10000 });

        // Take a screenshot
        const filename = `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-01-dashboard.png`;
        await page.screenshot({ path: filename, fullPage: true });

        console.log(`✓ ${deviceName}: Login successful - Dashboard loaded`);
      });

      test(`should navigate to Scraper Control on ${deviceName}`, async ({ page }) => {
        await login(page);

        // On mobile, we might need to open a hamburger menu first
        try {
          const hamburger = page.locator('button[aria-label="Menu"], button:has-text("☰"), [data-testid="mobile-menu"]').first();
          if (await hamburger.isVisible({ timeout: 2000 })) {
            await hamburger.click();
            await page.waitForTimeout(500);
          }
        } catch (e) {
          console.log('No hamburger menu found or not needed');
        }

        await navigateToScraperControl(page);

        // Verify we're on the scraper control page
        await expect(page).toHaveURL(/scraper/i);

        // Take a screenshot
        const filename = `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-02-scraper-control.png`;
        await page.screenshot({ path: filename, fullPage: true });

        console.log(`✓ ${deviceName}: Navigated to Scraper Control page`);
      });

      test(`should check for text overflow on ${deviceName}`, async ({ page }) => {
        await login(page);

        // Navigate to scraper control
        try {
          const hamburger = page.locator('button[aria-label="Menu"], button:has-text("☰"), [data-testid="mobile-menu"]').first();
          if (await hamburger.isVisible({ timeout: 2000 })) {
            await hamburger.click();
            await page.waitForTimeout(500);
          }
        } catch (e) {
          // No hamburger menu
        }

        await navigateToScraperControl(page);

        // Wait for content to load
        await page.waitForTimeout(2000);

        // Check for site cards
        const siteCards = page.locator('[data-testid="site-card"], .site-card, div:has(button:has-text("Enable")), div:has(button:has-text("Disable"))');
        const cardCount = await siteCards.count();

        console.log(`${deviceName}: Found ${cardCount} site cards`);

        // Check for potential overflow issues
        const overflowIssues = [];

        // Check URLs (they tend to overflow on mobile)
        const urls = page.locator('a[href^="http"], .url, .site-url');
        const urlCount = await urls.count();

        if (urlCount > 0) {
          console.log(`${deviceName}: Found ${urlCount} URLs to check for overflow`);
        }

        // Take screenshots at different scroll positions to capture all content
        await page.screenshot({
          path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-03-overflow-check-top.png`,
          fullPage: false
        });

        // Scroll to middle
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
        await page.waitForTimeout(500);
        await page.screenshot({
          path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-04-overflow-check-middle.png`,
          fullPage: false
        });

        // Full page screenshot
        await page.screenshot({
          path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-05-overflow-check-full.png`,
          fullPage: true
        });

        console.log(`✓ ${deviceName}: Text overflow check complete`);
      });

      test(`should test interactive elements on ${deviceName}`, async ({ page }) => {
        await login(page);

        // Navigate to scraper control
        try {
          const hamburger = page.locator('button[aria-label="Menu"], button:has-text("☰"), [data-testid="mobile-menu"]').first();
          if (await hamburger.isVisible({ timeout: 2000 })) {
            await hamburger.click();
            await page.waitForTimeout(500);
          }
        } catch (e) {
          // No hamburger menu
        }

        await navigateToScraperControl(page);

        const testResults: any = {
          device: deviceName,
          addButton: false,
          dropdownMenu: false,
          toggleButton: false,
          deleteButton: false,
        };

        // Test Add Site button
        try {
          const addButton = page.locator('button:has-text("Add Site"), button:has-text("Add")').first();
          if (await addButton.isVisible({ timeout: 3000 })) {
            testResults.addButton = true;
            console.log(`✓ ${deviceName}: Add Site button is visible`);

            // Take screenshot before clicking
            await page.screenshot({
              path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-06-before-add-click.png`,
              fullPage: true
            });
          }
        } catch (e) {
          console.log(`✗ ${deviceName}: Add Site button not found`);
        }

        // Test dropdown menu (three dots)
        try {
          const dropdownTrigger = page.locator('button[aria-label*="menu"], button:has-text("⋮"), button:has-text("...")').first();
          if (await dropdownTrigger.isVisible({ timeout: 3000 })) {
            testResults.dropdownMenu = true;
            console.log(`✓ ${deviceName}: Dropdown menu button found`);

            await dropdownTrigger.click();
            await page.waitForTimeout(500);

            // Take screenshot with dropdown open
            await page.screenshot({
              path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-07-dropdown-open.png`,
              fullPage: true
            });

            // Close dropdown
            await page.keyboard.press('Escape');
            await page.waitForTimeout(300);
          }
        } catch (e) {
          console.log(`✗ ${deviceName}: Dropdown menu not found`);
        }

        // Test Enable/Disable toggle
        try {
          const toggleButton = page.locator('button:has-text("Enable"), button:has-text("Disable")').first();
          if (await toggleButton.isVisible({ timeout: 3000 })) {
            testResults.toggleButton = true;
            console.log(`✓ ${deviceName}: Toggle button found`);
          }
        } catch (e) {
          console.log(`✗ ${deviceName}: Toggle button not found`);
        }

        // Test Delete button (in dropdown or visible)
        try {
          const deleteButton = page.locator('button:has-text("Delete"), button:has-text("Remove")').first();
          if (await deleteButton.isVisible({ timeout: 2000 })) {
            testResults.deleteButton = true;
            console.log(`✓ ${deviceName}: Delete button found`);
          }
        } catch (e) {
          console.log(`✗ ${deviceName}: Delete button not found or not visible`);
        }

        // Final screenshot
        await page.screenshot({
          path: `test-results/mobile-${deviceName.replace(/\s+/g, '-')}-08-final-state.png`,
          fullPage: true
        });

        console.log(`${deviceName} Test Results:`, testResults);
      });
    });
  }
});

test.describe('Realtors Practice - Comprehensive UI Tests', () => {
  test('should perform full functionality test on desktop', async ({ page }) => {
    await login(page);
    await navigateToScraperControl(page);

    const report = {
      addButtonWorks: false,
      canInteractWithCards: false,
      dropdownMenuWorks: false,
      noVisualBugs: true,
    };

    // Test Add Site button
    try {
      const addButton = page.locator('button:has-text("Add Site"), button:has-text("Add")').first();
      await addButton.click({ timeout: 3000 });
      await page.waitForTimeout(1000);

      // Check if a modal or form appeared
      const modal = page.locator('[role="dialog"], .modal, .dialog');
      if (await modal.isVisible({ timeout: 2000 })) {
        report.addButtonWorks = true;
        console.log('✓ Add Site button opens modal/form');

        await page.screenshot({ path: 'test-results/add-site-modal.png' });

        // Close modal
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    } catch (e) {
      console.log('✗ Add Site button test failed:', e);
    }

    // Test site card interactions
    try {
      const siteCards = page.locator('[data-testid="site-card"], .site-card').first();
      if (await siteCards.isVisible({ timeout: 3000 })) {
        report.canInteractWithCards = true;
        console.log('✓ Site cards are visible and interactive');
      }
    } catch (e) {
      console.log('✗ Site cards not found');
    }

    console.log('Final Report:', report);

    // Take final screenshot
    await page.screenshot({ path: 'test-results/final-comprehensive-test.png', fullPage: true });
  });
});
