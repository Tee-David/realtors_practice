const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 500 });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('=== Testing Theme Switch Functionality ===\n');

    // Navigate to the dashboard
    console.log('Navigating to dashboard...');
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);

    // Check initial theme
    console.log('\n=== Checking Initial Theme ===');
    const htmlElement = page.locator('html');
    const initialClass = await htmlElement.getAttribute('class');
    console.log(`Initial theme class: ${initialClass || 'none (light theme)'}`);

    // Take screenshot of initial state
    await page.screenshot({ path: 'frontend/theme-initial.png', fullPage: true });
    console.log('Screenshot saved: theme-initial.png');

    // Look for theme toggle button
    console.log('\n=== Looking for Theme Toggle ===');

    // Theme toggle should be in the sidebar footer
    const themeToggleButton = page.locator('button').filter({ has: page.locator('svg') });
    const count = await themeToggleButton.count();
    console.log(`Found ${count} buttons with SVG icons`);

    // Try to find the theme toggle - it might have moon/sun icon
    const possibleThemeToggles = await page.locator('button[aria-label*="theme" i], button[title*="theme" i]').count();
    console.log(`Found ${possibleThemeToggles} buttons with theme-related labels`);

    // Look in sidebar footer specifically
    const sidebarButtons = page.locator('[class*="sidebar"] button, [class*="footer"] button');
    const sidebarButtonCount = await sidebarButtons.count();
    console.log(`Found ${sidebarButtonCount} buttons in sidebar/footer`);

    // Try clicking what looks like a theme toggle
    // Usually it's a button with moon/sun SVG icon
    let themeToggle = null;

    // First, try to find by aria-label or title
    themeToggle = page.locator('button[aria-label*="theme" i]').first();
    let exists = await themeToggle.count() > 0;

    if (!exists) {
      // Try finding in sidebar footer
      console.log('Looking for theme toggle in sidebar footer...');

      // Look for buttons at the bottom of the sidebar
      themeToggle = page.locator('[class*="sidebar"]').locator('button').last();
      exists = await themeToggle.count() > 0;
    }

    if (exists) {
      console.log('\n=== Clicking Theme Toggle ===');

      const isVisible = await themeToggle.isVisible();
      console.log(`Theme toggle visible: ${isVisible}`);

      if (isVisible) {
        await themeToggle.click();
        console.log('Clicked theme toggle button');

        // Wait for theme change animation
        await page.waitForTimeout(1000);

        // Check new theme
        const newClass = await htmlElement.getAttribute('class');
        console.log(`New theme class: ${newClass || 'none (light theme)'}`);
        console.log(`Theme changed: ${initialClass !== newClass}`);

        // Take screenshot after first toggle
        await page.screenshot({ path: 'frontend/theme-toggled.png', fullPage: true });
        console.log('Screenshot saved: theme-toggled.png');

        // Toggle back
        console.log('\n=== Toggling Theme Back ===');
        await themeToggle.click();
        await page.waitForTimeout(1000);

        const finalClass = await htmlElement.getAttribute('class');
        console.log(`Final theme class: ${finalClass || 'none (light theme)'}`);
        console.log(`Returned to original: ${initialClass === finalClass}`);

        // Take screenshot after second toggle
        await page.screenshot({ path: 'frontend/theme-final.png', fullPage: true });
        console.log('Screenshot saved: theme-final.png');

        // Check localStorage for theme persistence
        const storedTheme = await page.evaluate(() => localStorage.getItem('theme'));
        console.log(`\n=== Theme Persistence ===`);
        console.log(`Stored theme in localStorage: ${storedTheme}`);

        console.log('\n✅ Theme switching test completed successfully!');
      } else {
        console.log('❌ Theme toggle button not visible');
      }
    } else {
      console.log('❌ Could not find theme toggle button');
      await page.screenshot({ path: 'frontend/theme-toggle-not-found.png', fullPage: true });
    }

    await page.waitForTimeout(2000);

  } catch (error) {
    console.error('\n=== ERROR ===');
    console.error(error.message);
    await page.screenshot({ path: 'frontend/error-theme-test.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();
