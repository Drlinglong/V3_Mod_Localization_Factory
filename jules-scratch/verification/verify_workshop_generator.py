import sys
from playwright.sync_api import sync_playwright, expect

def main():
    with sync_playwright() as p:
        try:
            # First, ensure browser dependencies are installed
            # This is typically done from the command line: playwright install
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the root of the React app
            print("Navigating to http://localhost:5173/...")
            page.goto("http://localhost:5173/", timeout=60000)

            # Click the 'Tools' link in the navigation
            print("Clicking 'Tools' navigation link...")
            page.get_by_role("link", name="Tools").click()

            # Wait for the page title to confirm navigation
            print("Waiting for 'Tools' page to load...")
            expect(page.locator('h1')).to_have_text('Tools', timeout=15000)

            # Click the 'Workshop Generator' tab
            print("Clicking 'Workshop Generator' tab...")
            page.get_by_role("tab", name="Workshop Generator").click()

            # Wait for a specific element within the WorkshopGenerator to be visible
            print("Waiting for Workshop Generator component to be visible...")
            expect(page.get_by_text("Steam Workshop Description Generator")).to_be_visible(timeout=10000)

            # Take a screenshot
            screenshot_path = "jules-scratch/verification/verification.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot taken successfully and saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            error_path = "jules-scratch/verification/error.png"
            # In case of error, save a screenshot for debugging
            if 'page' in locals():
                 page.screenshot(path=error_path)
                 print(f"Error screenshot saved to {error_path}", file=sys.stderr)
            sys.exit(1) # Exit with an error code
        finally:
            if 'browser' in locals() and browser.is_connected():
                browser.close()

if __name__ == "__main__":
    main()
