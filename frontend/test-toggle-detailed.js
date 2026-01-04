const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture console messages
  page.on('console', msg => {
    const type = msg.type();
    console.log(`BROWSER ${type.toUpperCase()}:`, msg.text());
  });

  // Capture network requests for toggle
  page.on('request', request => {
    if (request.url().includes('/toggle')) {
      console.log(`\n🔄 TOGGLE REQUEST: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', async response => {
    if (response.url().includes('/toggle')) {
      const status = response.status();
      console.log(`🔄 TOGGLE RESPONSE: ${status} ${response.url()}`);
      try {
        const body = await response.text();
        console.log(`🔄 TOGGLE RESPONSE BODY: ${body}`);
      } catch (e) {
        console.log('Could not read toggle response body');
      }
    }
  });

  try {
    console.log('=== Navigating to scraper control page ===');
    await page.goto('http://localhost:3000/scraper', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);

    console.log('\n=== Looking for sites in table ===');
    const tableRows = await page.locator('table tbody tr').count();
    console.log(`Found ${tableRows} site rows`);

    if (tableRows > 0) {
      // Get first site details
      const firstSiteText = await page.locator('table tbody tr:first-child td:nth-child(2)').textContent();
      console.log(`\nFirst site: ${firstSiteText.trim()}`);

      // Find the status of the first site
      const statusCell = await page.locator('table tbody tr:first-child td:nth-child(5)').textContent();
      console.log(`Current status: ${statusCell.trim()}`);

      // Find toggle button - it's the second button in the actions column (after Edit)
      console.log('\n=== Attempting to click toggle button ===');

      // Wait for buttons to be ready
      await page.waitForTimeout(1000);

      // Desktop view: Look for the toggle button (Power/PowerOff icon)
      const toggleButton = page.locator('table tbody tr:first-child td:last-child button').nth(1);
      const isVisible = await toggleButton.isVisible();
      console.log(`Toggle button visible: ${isVisible}`);

      if (isVisible) {
        // Take screenshot before click
        await page.screenshot({ path: 'frontend/before-toggle.png' });
        console.log('Screenshot saved: before-toggle.png');

        // Click the toggle button
        console.log('Clicking toggle button...');
        await toggleButton.click();

        // Wait for response
        await page.waitForTimeout(3000);

        // Take screenshot after click
        await page.screenshot({ path: 'frontend/after-toggle.png' });
        console.log('Screenshot saved: after-toggle.png');

        // Check for toast notifications
        const toasts = await page.locator('[class*="sonner"], [data-sonner-toast]').count();
        console.log(`\nToast notifications: ${toasts}`);

        if (toasts > 0) {
          // Wait a bit for toast to appear
          await page.waitForTimeout(1000);
          const toastElements = await page.locator('[class*="sonner"], [data-sonner-toast]').all();
          for (let i = 0; i < toastElements.length; i++) {
            const toastText = await toastElements[i].textContent();
            console.log(`Toast ${i + 1}: ${toastText}`);
          }
        }

        // Check new status
        await page.waitForTimeout(1000);
        const newStatusCell = await page.locator('table tbody tr:first-child td:nth-child(5)').textContent();
        console.log(`\nNew status: ${newStatusCell.trim()}`);
        console.log(`Status changed: ${statusCell.trim() !== newStatusCell.trim()}`);
      }
    } else {
      console.log('No sites found in table!');
    }

    await page.waitForTimeout(2000);

  } catch (error) {
    console.error('\n=== ERROR ===');
    console.error(error.message);
    await page.screenshot({ path: 'frontend/error-toggle-test.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
