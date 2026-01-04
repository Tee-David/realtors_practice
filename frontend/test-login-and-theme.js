const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 300 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('=== Testing Login and Theme Switch ===\n');

    // Navigate to the root (which shows login screen)
    console.log('Navigating to application...');
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000); // Wait for page loader

    console.log('\n=== Step 1: Login with Firebase ===');

    // Fill in email
    const emailInput = page.locator('#emailOrUsername');
    await emailInput.fill('testuser@realtorspractice.com');
    console.log('Filled email: testuser@realtorspractice.com');

    // Fill in password
    const passwordInput = page.locator('#password');
    await passwordInput.fill('Test123!');
    console.log('Filled password: Test123!');

    // Take screenshot before login
    await page.screenshot({ path: 'frontend/before-login.png', fullPage: true });
    console.log('Screenshot saved: before-login.png');

    // Click login button
    const loginButton = page.locator('button[type="submit"]:has-text("Log in")');
    await loginButton.click();
    console.log('Clicked login button');

    // Wait for navigation
    console.log('Waiting for authentication...');
    await page.waitForTimeout(8000); // Wait for login and navigation

    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);

    // Take screenshot after login
    await page.screenshot({ path: 'frontend/after-login.png', fullPage: true });
    console.log('Screenshot saved: after-login.png');

    // Check if we're logged in (should not be on login screen anymore)
    const isStillOnLogin = await page.locator('text="Welcome Back"').isVisible().catch(() => false);

    if (isStillOnLogin) {
      console.log('[ERROR] Still on login screen - login failed');

      // Check for error messages
      const errorToasts = await page.locator('[class*="sonner"], [data-sonner-toast]').count();
      if (errorToasts > 0) {
        const errorText = await page.locator('[class*="sonner"], [data-sonner-toast]').first().textContent();
        console.log(`Error message: ${errorText}`);
      }
    } else {
      console.log('[SUCCESS] Login successful! Now on dashboard\n');

      console.log('=== Step 2: Test Theme Switching ===');

      // Wait for dashboard to load
      await page.waitForTimeout(3000);

      // Check initial theme
      const htmlElement = page.locator('html');
      const initialClass = await htmlElement.getAttribute('class');
      const initialIsDark = initialClass?.includes('dark') || false;
      console.log(`Initial theme: ${initialIsDark ? 'dark' : 'light'}`);

      // Look for theme toggle button
      // The theme toggle should be in the sidebar footer
      // It's typically a button with sun/moon icon
      console.log('Looking for theme toggle button...');

      // Try to find in sidebar
      const sidebar = page.locator('[class*="sidebar"]');
      const sidebarExists = await sidebar.count() > 0;
      console.log(`Sidebar found: ${sidebarExists}`);

      if (sidebarExists) {
        // Get all buttons in sidebar
        const sidebarButtons = await sidebar.locator('button').all();
        console.log(`Buttons in sidebar: ${sidebarButtons.length}`);

        // The theme toggle is usually at the bottom, so try the last few buttons
        if (sidebarButtons.length > 0) {
          const lastButton = sidebar.locator('button').last();

          console.log('Attempting to click theme toggle...');
          await lastButton.click();
          console.log('Clicked potential theme toggle');

          await page.waitForTimeout(1000);

          // Check if theme changed
          const newClass = await htmlElement.getAttribute('class');
          const newIsDark = newClass?.includes('dark') || false;
          const themeChanged = initialIsDark !== newIsDark;

          console.log(`New theme: ${newIsDark ? 'dark' : 'light'}`);
          console.log(`Theme changed: ${themeChanged ? '[SUCCESS] YES' : '[FAILED] NO'}`);

          if (themeChanged) {
            // Take screenshot after theme change
            await page.screenshot({ path: 'frontend/theme-changed.png', fullPage: true });
            console.log('Screenshot saved: theme-changed.png');

            // Check localStorage
            const storedTheme = await page.evaluate(() => localStorage.getItem('theme'));
            console.log(`Theme persisted in localStorage: ${storedTheme}`);

            // Toggle back
            console.log('\nToggling theme back...');
            await lastButton.click();
            await page.waitForTimeout(1000);

            const finalClass = await htmlElement.getAttribute('class');
            const finalIsDark = finalClass?.includes('dark') || false;
            console.log(`Final theme: ${finalIsDark ? 'dark' : 'light'}`);
            console.log(`Returned to original: ${initialIsDark === finalIsDark ? '[SUCCESS] YES' : '[FAILED] NO'}`);

            await page.screenshot({ path: 'frontend/theme-final.png', fullPage: true });
            console.log('Screenshot saved: theme-final.png');

            console.log('\n[SUCCESS] Theme switching test completed successfully!');
          } else {
            console.log('\n[FAILED] Theme did not change - button might not be the theme toggle');
          }
        }
      } else {
        console.log('[ERROR] Sidebar not found');

        // Debug: Take screenshot to see the page structure
        await page.screenshot({ path: 'frontend/debug-no-sidebar.png', fullPage: true });
      }
    }

    await page.waitForTimeout(2000);

  } catch (error) {
    console.error('\n=== ERROR ===');
    console.error(error.message);
    await page.screenshot({ path: 'frontend/error.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
