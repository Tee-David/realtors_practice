"""
Mobile Playwright Test for Scraper Control Page - Manual Login Version
This version requires you to login manually, then it will run the tests
"""

import asyncio
from playwright.async_api import async_playwright, Page
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:3000"

# Mobile device configurations
MOBILE_DEVICES = [
    {
        "name": "iPhone SE",
        "viewport": {"width": 375, "height": 667},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    },
    {
        "name": "iPhone 12",
        "viewport": {"width": 390, "height": 844},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    },
    {
        "name": "Pixel 5",
        "viewport": {"width": 393, "height": 851},
        "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36"
    }
]

# Screenshot directory
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots", "mobile_scraper_control")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class MobileScraperControlTester:
    def __init__(self):
        self.results = []
        self.issues = []

    async def wait_for_manual_login(self, page: Page):
        """Wait for user to login manually"""
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("Please login to the application in the browser window.")
        print("Once you're logged in and see the dashboard, press Enter here...")
        print("="*60)

        # Open login page
        await page.goto(BASE_URL)

        # Wait for user to login
        input("\nPress Enter after you've logged in successfully...")

        # Verify we're logged in
        current_url = page.url
        if "dashboard" in current_url or "scraper" in current_url:
            print("Login verified!")
            return True
        else:
            print(f"Warning: Current URL is {current_url}")
            print("Continuing anyway...")
            return True

    async def navigate_to_scraper_control(self, page: Page, device_name: str):
        """Navigate to scraper control page"""
        print(f"  > Navigating to Scraper Control page")

        try:
            # Try direct navigation first
            await page.goto(f"{BASE_URL}/scraper-control")
            await page.wait_for_load_state("networkidle")

            # Verify we're on the right page
            current_url = page.url
            if "scraper-control" in current_url:
                print("  > Successfully navigated to Scraper Control page")
                return True

            # If direct navigation didn't work, try using the sidebar
            print("  > Trying sidebar navigation")

            # Check if sidebar is visible (desktop) or needs to be opened (mobile)
            sidebar_button = await page.query_selector('button[aria-label="Toggle sidebar"]')
            if sidebar_button:
                print("  > Opening mobile sidebar")
                await sidebar_button.click()
                await page.wait_for_timeout(500)

            # Look for Scraper Control link
            scraper_link = await page.query_selector('text="Scraper Control"')
            if scraper_link:
                await scraper_link.click()
                await page.wait_for_load_state("networkidle")
                print("  > Navigated via sidebar link")
                return True

            print("  X Could not find Scraper Control navigation")
            return False

        except Exception as e:
            print(f"  X Navigation error: {e}")
            return False

    async def test_site_cards_layout(self, page: Page, device_name: str):
        """Test site cards for text overflow and truncation"""
        print(f"  > Testing site cards layout")

        issues = []

        try:
            # Wait for site cards to load
            await page.wait_for_selector('[data-testid="site-card"], .site-card, [class*="card"]', timeout=10000)

            # Take full page screenshot
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{device_name.replace(' ', '_')}_full_page.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  > Screenshot saved: {screenshot_path}")

            # Get all site cards
            cards = await page.query_selector_all('[data-testid="site-card"], .site-card, [class*="card"]')
            print(f"  > Found {len(cards)} site cards")

            if len(cards) == 0:
                # Try alternative selectors
                cards = await page.query_selector_all('div:has(button:has-text("Enable")), div:has(button:has-text("Disable"))')
                print(f"  > Found {len(cards)} cards using alternative selector")

            # Test first 5 cards in detail
            for idx, card in enumerate(cards[:5]):
                card_issues = await self.check_card_overflow(page, card, idx, device_name)
                issues.extend(card_issues)

        except Exception as e:
            print(f"  X Error testing site cards: {e}")
            issues.append({
                "device": device_name,
                "type": "error",
                "element": "site-cards",
                "issue": str(e)
            })

        return issues

    async def check_card_overflow(self, page: Page, card, idx: int, device_name: str):
        """Check a single card for overflow issues"""
        issues = []

        try:
            # Scroll card into view
            await card.scroll_into_view_if_needed()
            await page.wait_for_timeout(200)

            # Take screenshot of the card
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{device_name.replace(' ', '_')}_card_{idx}.png")
            await card.screenshot(path=screenshot_path)

            # Get card dimensions
            box = await card.bounding_box()
            if box:
                # Check for horizontal scrollbar (indicates overflow)
                scroll_width = await card.evaluate("el => el.scrollWidth")
                client_width = await card.evaluate("el => el.clientWidth")

                if scroll_width > client_width:
                    issues.append({
                        "device": device_name,
                        "type": "horizontal_overflow",
                        "element": f"card_{idx}",
                        "scroll_width": scroll_width,
                        "client_width": client_width,
                        "screenshot": screenshot_path
                    })
                    print(f"  ! Card {idx}: Horizontal overflow detected ({scroll_width}px > {client_width}px)")

        except Exception as e:
            print(f"  X Error checking card {idx}: {e}")

        return issues

    async def test_buttons(self, page: Page, device_name: str):
        """Test button functionality and responsiveness"""
        print(f"  > Testing buttons")

        issues = []

        try:
            # Define buttons to test
            button_selectors = [
                ('Add Site', 'button:has-text("Add Site"), button:has-text("Add")'),
                ('Enable', 'button:has-text("Enable")'),
                ('Disable', 'button:has-text("Disable")'),
                ('Delete', 'button:has-text("Delete")'),
                ('Enable All', 'button:has-text("Enable All")'),
                ('Disable All', 'button:has-text("Disable All")'),
            ]

            for button_name, selector in button_selectors:
                buttons = await page.query_selector_all(selector)

                if len(buttons) == 0:
                    print(f"  ! No '{button_name}' buttons found")
                    continue

                print(f"  > Found {len(buttons)} '{button_name}' button(s)")

                # Test first button of each type
                button = buttons[0]

                # Get button dimensions
                box = await button.bounding_box()

                if box:
                    # Check if button is too small for mobile (minimum 44x44px for touch targets)
                    if box["width"] < 44 or box["height"] < 44:
                        issues.append({
                            "device": device_name,
                            "type": "button_too_small",
                            "button": button_name,
                            "width": box["width"],
                            "height": box["height"]
                        })
                        print(f"  ! {button_name}: Too small ({box['width']}x{box['height']}px)")

                    # Check if button text is truncated
                    text = await button.inner_text()
                    is_truncated = await button.evaluate("el => el.scrollWidth > el.clientWidth")

                    if is_truncated:
                        issues.append({
                            "device": device_name,
                            "type": "button_text_truncated",
                            "button": button_name,
                            "text": text
                        })
                        print(f"  ! {button_name}: Text truncated")

                # Take screenshot of button area
                if box:
                    screenshot_path = os.path.join(
                        SCREENSHOT_DIR,
                        f"{device_name.replace(' ', '_')}_button_{button_name.replace(' ', '_')}.png"
                    )
                    await button.screenshot(path=screenshot_path)

        except Exception as e:
            print(f"  X Error testing buttons: {e}")
            issues.append({
                "device": device_name,
                "type": "error",
                "element": "buttons",
                "issue": str(e)
            })

        return issues

    async def test_device(self, device_config: dict):
        """Test on a specific mobile device"""
        device_name = device_config["name"]
        print(f"\n{'='*60}")
        print(f"Testing on {device_name}")
        print(f"Viewport: {device_config['viewport']['width']}x{device_config['viewport']['height']}")
        print(f"{'='*60}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)

            context = await browser.new_context(
                viewport=device_config["viewport"],
                user_agent=device_config.get("user_agent", "")
            )

            page = await context.new_page()

            try:
                # Manual login (only for first device)
                if device_name == MOBILE_DEVICES[0]["name"]:
                    if not await self.wait_for_manual_login(page):
                        self.issues.append({
                            "device": device_name,
                            "type": "login_failed",
                            "issue": "Could not login to application"
                        })
                        return

                # Navigate to scraper control
                if not await self.navigate_to_scraper_control(page, device_name):
                    self.issues.append({
                        "device": device_name,
                        "type": "navigation_failed",
                        "issue": "Could not navigate to Scraper Control page"
                    })
                    return

                # Take initial screenshot
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{device_name.replace(' ', '_')}_initial.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"  > Initial screenshot: {screenshot_path}")

                # Run tests
                card_issues = await self.test_site_cards_layout(page, device_name)
                self.issues.extend(card_issues)

                button_issues = await self.test_buttons(page, device_name)
                self.issues.extend(button_issues)

                # Take final screenshot
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"{device_name.replace(' ', '_')}_final.png")
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"  > Final screenshot: {screenshot_path}")

                print(f"\nOK Testing completed for {device_name}")

            except Exception as e:
                print(f"\nX Error testing {device_name}: {e}")
                self.issues.append({
                    "device": device_name,
                    "type": "test_error",
                    "issue": str(e)
                })

            finally:
                await browser.close()

    async def run_all_tests(self):
        """Run tests on all mobile devices"""
        print("\n" + "="*60)
        print("MOBILE SCRAPER CONTROL PAGE TESTING")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        for device in MOBILE_DEVICES:
            await self.test_device(device)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)

        print(f"\nTotal issues found: {len(self.issues)}")

        if len(self.issues) == 0:
            print("\nOK No issues found! The page is mobile-responsive.")
        else:
            # Group issues by type
            issues_by_type = {}
            for issue in self.issues:
                issue_type = issue.get("type", "unknown")
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)

            print("\nIssues by type:")
            for issue_type, issues in issues_by_type.items():
                print(f"\n{issue_type.upper().replace('_', ' ')} ({len(issues)}):")
                for issue in issues:
                    device = issue.get("device", "Unknown")
                    element = issue.get("element", issue.get("button", "Unknown"))
                    print(f"  * {device}: {element}")

                    # Print additional details
                    for key, value in issue.items():
                        if key not in ["device", "type", "element", "button"]:
                            print(f"    - {key}: {value}")

        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print("\n" + "="*60)

async def main():
    """Main test runner"""
    tester = MobileScraperControlTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
