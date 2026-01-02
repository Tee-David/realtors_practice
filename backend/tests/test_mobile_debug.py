"""
Simple debug script to see what's happening with the login
"""

import asyncio
from playwright.async_api import async_playwright
import os

BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots", "debug")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        # iPhone SE viewport
        context = await browser.new_context(
            viewport={"width": 375, "height": 667}
        )

        page = await context.new_page()

        print("Navigating to login page...")
        await page.goto(BASE_URL)

        # Wait for page load
        await page.wait_for_timeout(3000)

        # Take screenshot of login page
        screenshot_path = os.path.join(SCREENSHOT_DIR, "01_login_page.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved: {screenshot_path}")

        # Try to fill the form
        print("\nLooking for email field...")
        email_field = await page.query_selector('input[type="email"]')
        if email_field:
            print("Found email field, filling...")
            await email_field.fill("admin@realtorspractice.com")
            await page.wait_for_timeout(500)

        print("\nLooking for password field...")
        password_field = await page.query_selector('input[type="password"]')
        if password_field:
            print("Found password field, filling...")
            await password_field.fill("Password123!")
            await page.wait_for_timeout(500)

        # Take screenshot after filling
        screenshot_path = os.path.join(SCREENSHOT_DIR, "02_form_filled.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved: {screenshot_path}")

        # Look for login button
        print("\nLooking for login button...")
        login_button = await page.query_selector('button[type="submit"]')
        if login_button:
            button_text = await login_button.inner_text()
            print(f"Found button: {button_text}")

            print("Clicking login button...")
            await login_button.click()

            # Wait for response
            await page.wait_for_timeout(5000)

            # Take screenshot after click
            screenshot_path = os.path.join(SCREENSHOT_DIR, "03_after_login_click.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            # Check URL
            print(f"Current URL: {page.url}")

            # Check for any error messages
            page_content = await page.content()
            if "error" in page_content.lower() or "invalid" in page_content.lower():
                print("Possible error on page")

                # Try to find error message
                error_elements = await page.query_selector_all('[role="alert"], .error, [class*="error"]')
                for elem in error_elements:
                    text = await elem.inner_text()
                    if text:
                        print(f"Error message: {text}")

        print("\nWaiting 10 seconds for manual inspection...")
        await page.wait_for_timeout(10000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
