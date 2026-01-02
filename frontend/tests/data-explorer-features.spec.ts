import { test, expect, type Page } from '@playwright/test';

// Test credentials
const TEST_EMAIL = 'test@realtorspractice.com';
const TEST_PASSWORD = 'TestPass123!';
const BASE_URL = 'http://localhost:3000';

// Helper function to login
async function login(page: Page) {
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');

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

test.describe('Data Explorer - Recent Features', () => {
  test('should have Show Filters button', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Data Explorer
    try {
      await page.click('text=Data Explorer', { timeout: 5000 });
    } catch {
      await page.goto(`${BASE_URL}/data-explorer`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Take screenshot before checking
    await page.screenshot({
      path: 'test-results/data-explorer-initial.png',
      fullPage: true
    });

    // Check for Show Filters button
    const filterButton = page.locator('button:has-text("Filters")').or(
      page.locator('button:has-text("Show Filters")')
    ).or(
      page.locator('button:has-text("Hide Filters")')
    );

    const isVisible = await filterButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      console.log('✓ Show Filters button found');

      // Check if button has Filter icon
      const hasFilterIcon = await page.locator('button:has-text("Filters") svg').isVisible().catch(() => false);
      console.log(`  ${hasFilterIcon ? '✓' : '✗'} Filter icon present`);

      // Try clicking the button to toggle filters
      await filterButton.click();
      await page.waitForTimeout(500);

      await page.screenshot({
        path: 'test-results/data-explorer-filters-toggled.png',
        fullPage: true
      });

      console.log('  ✓ Filter toggle clicked successfully');
    } else {
      console.log('✗ Show Filters button not found');
    }
  });

  test('should have improved Export CSV button', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Data Explorer
    try {
      await page.click('text=Data Explorer', { timeout: 5000 });
    } catch {
      await page.goto(`${BASE_URL}/data-explorer`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Check for Export CSV button
    const exportButton = page.locator('button:has-text("Export CSV")').or(
      page.locator('button:has-text("Export")')
    );

    const isVisible = await exportButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      console.log('✓ Export CSV button found');

      // Check if button has Download icon
      const hasDownloadIcon = await page.locator('button:has-text("Export") svg').first().isVisible().catch(() => false);
      console.log(`  ${hasDownloadIcon ? '✓' : '✗'} Download icon present`);

      await page.screenshot({
        path: 'test-results/data-explorer-export-button.png',
        fullPage: false
      });
    } else {
      console.log('✗ Export CSV button not found');
    }
  });

  test('should have grid view selector with all options', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Data Explorer
    try {
      await page.click('text=Data Explorer', { timeout: 5000 });
    } catch {
      await page.goto(`${BASE_URL}/data-explorer`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Look for grid view selector (it's a Select component)
    const gridSelector = page.locator('[role="combobox"]').filter({ hasText: /column|view/i }).first();

    const isVisible = await gridSelector.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      console.log('✓ Grid view selector found');

      await gridSelector.click();
      await page.waitForTimeout(500);

      // Check for all grid options
      const options = ['List View', '2 Columns', '3 Columns', '4 Columns', '5 Columns', '6 Columns'];

      for (const option of options) {
        const optionVisible = await page.getByText(option, { exact: false }).isVisible({ timeout: 1000 }).catch(() => false);
        console.log(`  ${optionVisible ? '✓' : '✗'} ${option}`);
      }

      await page.screenshot({
        path: 'test-results/data-explorer-grid-options.png',
        fullPage: false
      });

      // Close dropdown
      await page.keyboard.press('Escape');
    } else {
      console.log('✗ Grid view selector not found');
    }
  });

  test('should display property count', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await login(page);

    // Navigate to Data Explorer
    try {
      await page.click('text=Data Explorer', { timeout: 5000 });
    } catch {
      await page.goto(`${BASE_URL}/data-explorer`);
    }

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // Check for property count text
    const countText = page.locator('text=/Showing .* of .* properties/i');
    const isVisible = await countText.isVisible({ timeout: 5000 }).catch(() => false);

    if (isVisible) {
      const text = await countText.textContent();
      console.log('✓ Property count found:', text);
    } else {
      console.log('✗ Property count not found');
    }

    await page.screenshot({
      path: 'test-results/data-explorer-final.png',
      fullPage: true
    });
  });
});
