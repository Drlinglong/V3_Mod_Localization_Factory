import os
import time
from playwright.sync_api import sync_playwright, expect

def verify_glossary_search():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("Navigating to app...")
        try:
            # Using hash router path
            page.goto("http://localhost:5173/#/glossary-manager", timeout=30000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        print("Page title:", page.title())

        print("Waiting for Glossary Manager content...")
        try:
            # Wait for "Glossary Manager" header
            page.wait_for_selector("h4", timeout=10000)

            print("Verifying Search Scope UI...")
            # Take screenshot of initial state
            page.screenshot(path="jules-scratch/glossary_page_initial.png")
            print("Screenshot saved to jules-scratch/glossary_page_initial.png")

            # Verify Scrolling layout
            container = page.locator("div[class*='pageContainer']")
            if container.count() > 0:
                box = container.bounding_box()
                print(f"Page Container Height: {box['height']}")

            # Perform Search
            print("Performing search...")

            # Type in search box
            filter_input = page.get_by_placeholder("Filter...")
            if filter_input.count() > 0:
                filter_input.fill("Apple")
            else:
                print("Filter input not found.")

            # Try to interact with Scope Select if possible
            # It might default to 'Current File'.
            # We can try to click the Select to see options.
            comboboxes = page.get_by_role("combobox")
            if comboboxes.count() > 1:
                # Usually 1st is Game, 2nd is Lang, 3rd is Scope?
                # Or check values.
                pass

            time.sleep(1)
            page.screenshot(path="jules-scratch/glossary_search_results.png")
            print("Screenshot saved to jules-scratch/glossary_search_results.png")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="jules-scratch/error_state.png")
            print("Saved error_state.png")

        browser.close()

if __name__ == "__main__":
    verify_glossary_search()
