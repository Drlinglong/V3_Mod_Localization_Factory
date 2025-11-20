import time
from playwright.sync_api import sync_playwright

def verify_themes():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Navigating to Settings page...")
        # Navigate to the app - assuming port 5173 as per command
        try:
            page.goto("http://localhost:5173/", timeout=60000)
            # Wait for app to load
            page.wait_for_selector("body", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        print("Page loaded. checking for burger menu or nav...")

        # Try to open settings page
        # First, if the nav is hidden (mobile view), we might need to open it, but viewport is 1280 wide

        # Find settings link. It usually has an icon or text "Settings"
        # Based on App.jsx, path is /settings

        # Navigate directly to settings to save time and avoid nav issues
        print("Navigating directly to /settings...")
        page.goto("http://localhost:5173/settings")
        time.sleep(2) # Give it a moment to render

        # Take screenshot of Default (Dark/Victorian?)
        page.screenshot(path="verification/theme_initial.png")
        print("Initial screenshot taken.")

        # Select Theme Dropdown
        # In SettingsPage.jsx (assumed), there should be a way to change theme.
        # Or usually in the header/navbar.
        # Let's check if we can find a theme toggler.
        # If not in settings, it might be in a user menu.

        # Let's assume there is a theme selector in SettingsPage.
        # If not, we might need to inspect the page content.

        # Let's try to find the 'Select theme' or similar input.
        # Using generic locators first

        # Actually, let's just verify the GlobalStyles component is present and has the class.
        background_layer = page.locator(".global-background-layer")

        if background_layer.count() > 0:
            print("Global background layer found!")
            # Get current class
            classes = background_layer.get_attribute("class")
            print(f"Current classes: {classes}")
        else:
            print("Global background layer NOT found!")

        # Function to change theme via JS if UI is hard to locate blindly
        def set_theme(theme_name):
            print(f"Attempting to set theme to {theme_name}...")
            # access the localStorage and reload, or try to find the UI.
            # LocalStorage is used in ThemeContext.
            page.evaluate(f"localStorage.setItem('theme', '{theme_name}')")
            page.reload()
            time.sleep(2)
            page.screenshot(path=f"verification/theme_{theme_name}.png")

            # Verify class
            layer = page.locator(".global-background-layer")
            if layer.count() > 0:
                cls = layer.get_attribute("class")
                print(f"Theme {theme_name} - Classes: {cls}")
                # Check computed style for background image
                bg_image = layer.evaluate("el => window.getComputedStyle(el).backgroundImage")
                print(f"Theme {theme_name} - BG Image: {bg_image[:50]}...") # print first 50 chars

        # Test all 5 themes
        themes = ['victorian', 'byzantine', 'scifi', 'wwii', 'medieval']

        for theme in themes:
            set_theme(theme)

        browser.close()

if __name__ == "__main__":
    verify_themes()
