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
            page.goto("http://localhost:5173/glossary-manager", timeout=60000)
            # Wait for app to load
            page.wait_for_selector("body", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        print("Page loaded.")
        time.sleep(3) # Give it a moment to render

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
            # New logic uses data-theme attribute, but ThemeContext updates it based on localStorage
            page.evaluate(f"localStorage.setItem('theme', '{theme_name}')")
            page.reload()
            time.sleep(3)

            # Verify data-theme attribute
            data_theme = page.evaluate("document.documentElement.getAttribute('data-theme')")
            print(f"Theme {theme_name} - HTML data-theme: {data_theme}")

            # Check Title Font Family (should be distinct for each theme)
            # e.g. SciFi -> Orbitron, Victorian -> Playfair Display
            title_font = get_computed_style("h4", "font-family")
            print(f"Theme {theme_name} - Title Font: {title_font}")

            # Check if background image (from GlobalStyles) is visible through transparent panels
            # We check the panel's background color - it should be an rgba value
            # Note: Because we used CSS modules, we need to find the element by class or structure
            # The panels are Paper components inside Grid Cols.
            # Let's look for the first Paper inside a Grid Col
            panel_bg = page.evaluate("""() => {
                const panel = document.querySelector('.mantine-Paper-root');
                return window.getComputedStyle(panel).backgroundColor;
            }""")
            print(f"Theme {theme_name} - Panel BG: {panel_bg}")

            page.screenshot(path=f"verification/glossary_theme_{theme_name}.png")

        # Test all 5 themes
        themes = ['victorian', 'byzantine', 'scifi', 'wwii', 'medieval']

        for theme in themes:
            set_theme(theme)

        browser.close()

if __name__ == "__main__":
    verify_themes()
