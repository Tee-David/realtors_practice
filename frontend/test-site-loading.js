const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture console messages
  page.on('console', msg => {
    const type = msg.type();
    if (type === 'error' || type === 'warning') {
      console.log(`BROWSER ${type.toUpperCase()}:`, msg.text());
    }
  });

  // Capture network requests
  const networkRequests = [];
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      networkRequests.push({
        url: request.url(),
        method: request.method()
      });
      console.log(`REQUEST: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', async response => {
    if (response.url().includes('/api/')) {
      const status = response.status();
      console.log(`RESPONSE: ${response.status()} ${response.url()}`);

      if (response.url().includes('/api/sites') && !response.url().includes('/toggle')) {
        try {
          const body = await response.text();
          console.log(`Sites API Response: ${body.substring(0, 200)}...`);
        } catch (e) {
          console.log('Could not read response body');
        }
      }
    }
  });

  try {
    console.log('\n=== Navigating to scraper control page ===');
    await page.goto('http://localhost:3000/scraper', { waitUntil: 'networkidle' });

    // Wait for potential data loading
    await page.waitForTimeout(5000);

    console.log('\n=== Checking page elements ===');

    // Check for loading state
    const loadingElements = await page.locator('text=/Loading|loading/i').count();
    console.log(`Loading indicators: ${loadingElements}`);

    // Check for error messages
    const errorElements = await page.locator('text=/Error|error|failed/i').count();
    console.log(`Error messages: ${errorElements}`);

    if (errorElements > 0) {
      const errorText = await page.locator('text=/Error|error|failed/i').first().textContent();
      console.log(`First error message: ${errorText}`);
    }

    // Check for site configuration section
    const siteConfigHeader = await page.locator('text=/Site Configuration/i').count();
    console.log(`Site Configuration header found: ${siteConfigHeader > 0}`);

    // Check for table
    const tables = await page.locator('table').count();
    console.log(`Tables found: ${tables}`);

    if (tables > 0) {
      const tableRows = await page.locator('table tbody tr').count();
      console.log(`Table rows: ${tableRows}`);

      if (tableRows === 0) {
        // Check if there's an empty state message
        const emptyState = await page.locator('text=/No sites|Add|Empty/i').count();
        console.log(`Empty state messages: ${emptyState}`);
        if (emptyState > 0) {
          const emptyStateText = await page.locator('text=/No sites|Add|Empty/i').first().textContent();
          console.log(`Empty state message: ${emptyStateText}`);
        }
      }
    }

    // Check for mobile cards (alternative to table on mobile)
    const mobileCards = await page.locator('[class*="md:hidden"]').count();
    console.log(`Mobile card containers: ${mobileCards}`);

    console.log('\n=== Network Requests Summary ===');
    console.log(`Total API requests made: ${networkRequests.length}`);
    networkRequests.forEach(req => {
      console.log(`  - ${req.method} ${req.url}`);
    });

    console.log('\n=== Taking screenshots ===');
    await page.screenshot({ path: 'frontend/scraper-page-debug.png', fullPage: true });
    console.log('Screenshot saved: scraper-page-debug.png');

    // Check localStorage and sessionStorage
    const apiUrl = await page.evaluate(() => localStorage.getItem('NEXT_PUBLIC_API_URL') || window.ENV?.NEXT_PUBLIC_API_URL);
    console.log(`\n=== Environment ===`);
    console.log(`API URL from storage/env: ${apiUrl}`);

    await page.waitForTimeout(2000);

  } catch (error) {
    console.error('\n=== ERROR ===');
    console.error(error);
    await page.screenshot({ path: 'frontend/error-screenshot.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
