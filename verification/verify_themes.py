import time
from playwright.sync_api import sync_playwright

def verify_themes():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Navigating to Glossary Manager page...")
        try:
            # Go to glossary manager to check the specific page refactoring
            page.goto("http://localhost:5173/glossary-manager", timeout=60000)
            # Wait for app to load
            page.wait_for_selector("body", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        print("Page loaded.")
        time.sleep(3) # Give it a moment to render the glossary content

        # Function to check computed style property
        def get_computed_style(selector, property_name):
            value = page.evaluate(f"""() => {{
                const el = document.querySelector('{selector}');
                if (!el) return "ELEMENT_NOT_FOUND";
                return window.getComputedStyle(el).getPropertyValue('{property_name}');
            }}""")
            return value

        # Function to change theme via JS
        def set_theme(theme_name):
            print(f"Attempting to set theme to {theme_name}...")
            page.evaluate(f"localStorage.setItem('theme', '{theme_name}')")
            page.reload()
            time.sleep(3) # Wait for reload and render

            # Check specific element styles on Glossary Manager Page
            # We expect the main panels (Paper components) to have changed styles.
            # We didn't assign a unique ID, but they are likely divs inside grid cols.
            # Let's look for a generic text or button to see font/color changes.

            # Check Title Font Family (should be var(--font-header))
            title_font = get_computed_style("h4.mantine-Title-root", "font-family")
            print(f"Theme {theme_name} - Title Font: {title_font}")

            # Check Button Background (should be var(--primary-color) or gradient)
            # Finding the "Add Entry" button or similar
            button_color = get_computed_style("button.mantine-Button-root", "color")
            print(f"Theme {theme_name} - Button Text Color: {button_color}")

            page.screenshot(path=f"verification/glossary_theme_{theme_name}.png")

        # Test all 5 themes
        themes = ['victorian', 'byzantine', 'scifi', 'wwii', 'medieval']

        for theme in themes:
            set_theme(theme)

        browser.close()

if __name__ == "__main__":
    verify_themes()
