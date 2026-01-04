const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('Navigating to scraper control page...');
    await page.goto('http://localhost:3000/scraper');

    // Wait for the page to load
    await page.waitForTimeout(3000);

    console.log('Taking screenshot of initial state...');
    await page.screenshot({ path: 'scraper-initial.png', fullPage: true });

    // Look for site configuration section
    console.log('Looking for site table...');
    const siteRows = await page.locator('table tbody tr').count();
    console.log(`Found ${siteRows} site rows`);

    // Try to find and click the first toggle button
    if (siteRows > 0) {
      console.log('Looking for toggle buttons...');

      // Look for Power or PowerOff icons (toggle buttons)
      const toggleButtons = page.locator('button[class*="ghost"]').filter({ has: page.locator('svg') });
      const count = await toggleButtons.count();
      console.log(`Found ${count} toggle-like buttons`);

      if (count > 0) {
        // Get the first site's details
        const firstSiteName = await page.locator('table tbody tr:first-child td:nth-child(2)').textContent();
        console.log(`First site: ${firstSiteName}`);

        // Try to click the toggle button for the first site
        console.log('Attempting to click toggle button...');
        const firstToggle = page.locator('table tbody tr:first-child button').nth(1); // Second button should be toggle

        // Take screenshot before click
        await page.screenshot({ path: 'before-toggle-click.png', fullPage: true });

        await firstToggle.click();
        console.log('Clicked toggle button');

        // Wait for potential network request
        await page.waitForTimeout(2000);

        // Take screenshot after click
        await page.screenshot({ path: 'after-toggle-click.png', fullPage: true });

        console.log('Screenshots saved: scraper-initial.png, before-toggle-click.png, after-toggle-click.png');
      }
    }

    // Check for any toast notifications
    const toasts = await page.locator('[class*="toast"], [class*="sonner"]').count();
    if (toasts > 0) {
      console.log(`Found ${toasts} toast notification(s)`);
      const toastText = await page.locator('[class*="toast"], [class*="sonner"]').first().textContent();
      console.log(`Toast message: ${toastText}`);
    }

    // Check console for any errors
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));

    await page.waitForTimeout(3000);

  } catch (error) {
    console.error('Error during test:', error);
    await page.screenshot({ path: 'error-screenshot.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
