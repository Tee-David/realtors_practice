const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 300 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('=== Testing with Firebase Login ===\n');

    // Navigate to the login page
    console.log('Navigating to login page...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);

    // Take screenshot of login page
    await page.screenshot({ path: 'frontend/login-page.png', fullPage: true });
    console.log('Screenshot saved: login-page.png');

    // Fill in login credentials
    console.log('\n=== Logging in with Firebase ===');

    // Find email input
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    await emailInput.fill('admin@realtorspractice.com');
    console.log('Filled email: admin@realtorspractice.com');

    // Find password input
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    await passwordInput.fill('admin123');
    console.log('Filled password: admin123');

    // Take screenshot before login
    await page.screenshot({ path: 'frontend/before-login.png', fullPage: true });

    // Click login button
    const loginButton = page.locator('button[type="submit"], button:has-text("Log in"), button:has-text("Sign in")').first();
    await loginButton.click();
    console.log('Clicked login button');

    // Wait for navigation to dashboard
    console.log('Waiting for navigation...');
    await page.waitForURL('**/dashboard', { timeout: 10000 }).catch(() => {
      console.log('Did not navigate to /dashboard, checking current URL...');
    });

    await page.waitForTimeout(3000);

    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);

    // Take screenshot after login
    await page.screenshot({ path: 'frontend/after-login.png', fullPage: true });
    console.log('Screenshot saved: after-login.png');

    if (currentUrl.includes('dashboard') || currentUrl === 'http://localhost:3000/') {
      console.log('✅ Successfully logged in!');

      // Now test theme switching
      console.log('\n=== Testing Theme Switch ===');

      // Check initial theme
      const htmlElement = page.locator('html');
      const initialClass = await htmlElement.getAttribute('class');
      console.log(`Initial theme: ${initialClass?.includes('dark') ? 'dark' : 'light'}`);

      // Look for theme toggle in sidebar
      console.log('Looking for theme toggle...');

      // Try multiple selectors for theme toggle
      let themeToggle = page.locator('button').filter({ hasText: /theme/i }).first();
      let count = await themeToggle.count();

      if (count === 0) {
        // Try finding by icon (Sun/Moon)
        themeToggle = page.locator('button').filter({ has: page.locator('svg') }).filter({ hasText: '' });
        count = await themeToggle.count();
        console.log(`Found ${count} icon-only buttons`);
      }

      // Try looking specifically in sidebar
      if (count === 0) {
        themeToggle = page.locator('[class*="sidebar"]').locator('button').last();
        count = await themeToggle.count();
        console.log(`Looking in sidebar, found ${count} buttons`);
      }

      if (count > 0) {
        const isVisible = await themeToggle.isVisible();
        console.log(`Theme toggle visible: ${isVisible}`);

        if (isVisible) {
          // Click theme toggle
          await themeToggle.click();
          console.log('Clicked theme toggle');

          await page.waitForTimeout(1000);

          const newClass = await htmlElement.getAttribute('class');
          console.log(`New theme: ${newClass?.includes('dark') ? 'dark' : 'light'}`);

          const themeChanged = (initialClass?.includes('dark')) !== (newClass?.includes('dark'));
          console.log(`Theme changed: ${themeChanged ? '✅ YES' : '❌ NO'}`);

          // Take screenshot after theme change
          await page.screenshot({ path: 'frontend/theme-changed.png', fullPage: true });
          console.log('Screenshot saved: theme-changed.png');

          // Check localStorage
          const storedTheme = await page.evaluate(() => localStorage.getItem('theme'));
          console.log(`Theme in localStorage: ${storedTheme}`);
        }
      } else {
        console.log('❌ Theme toggle not found');

        // Debug: list all buttons
        const allButtons = await page.locator('button').all();
        console.log(`\nTotal buttons on page: ${allButtons.length}`);

        for (let i = 0; i < Math.min(allButtons.length, 10); i++) {
          const text = await allButtons[i].textContent();
          const ariaLabel = await allButtons[i].getAttribute('aria-label');
          console.log(`  Button ${i + 1}: text="${text?.trim()}", aria-label="${ariaLabel}"`);
        }
      }
    } else {
      console.log('❌ Login failed - not on dashboard');
    }

    await page.waitForTimeout(3000);

  } catch (error) {
    console.error('\n=== ERROR ===');
    console.error(error.message);
    console.error(error.stack);
    await page.screenshot({ path: 'frontend/error.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
