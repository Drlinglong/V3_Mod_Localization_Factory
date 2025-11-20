import time
from playwright.sync_api import sync_playwright

def verify_themes():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Navigating to Settings page...")
        try:
            page.goto("http://localhost:5173/settings", timeout=60000)
            # Wait for app to load
            page.wait_for_selector("body", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            browser.close()
            return

        print("Page loaded.")
        time.sleep(2) # Give it a moment to render

        # Function to check background transparency of AppShell
        def check_transparency(element_selector):
            bg_color = page.evaluate(f"""() => {{
                const el = document.querySelector('{element_selector}');
                if (!el) return "ELEMENT_NOT_FOUND";
                return window.getComputedStyle(el).backgroundColor;
            }}""")
            return bg_color

        # Check AppShell Main Transparency
        main_bg = check_transparency(".mantine-AppShell-main")
        print(f"AppShell Main BG Color: {main_bg}")

        if main_bg != "rgba(0, 0, 0, 0)" and main_bg != "transparent":
             print("WARNING: AppShell Main is NOT transparent!")
        else:
             print("SUCCESS: AppShell Main is transparent.")

        # Function to change theme via JS
        def set_theme(theme_name):
            print(f"Attempting to set theme to {theme_name}...")
            page.evaluate(f"localStorage.setItem('theme', '{theme_name}')")
            page.reload()
            time.sleep(2)

            # Verify global background layer exists
            layer = page.locator(".global-background-layer")
            if layer.count() > 0:
                cls = layer.get_attribute("class")
                print(f"Theme {theme_name} - Classes: {cls}")

                # Check sidebar transparency
                # The sidebar in Mantine AppShell typically has class .mantine-AppShell-navbar
                sidebar_bg = check_transparency(".mantine-AppShell-navbar")
                print(f"Theme {theme_name} - Sidebar BG: {sidebar_bg}")

            page.screenshot(path=f"verification/theme_{theme_name}_transparent.png")

        # Test all 5 themes
        themes = ['victorian', 'byzantine', 'scifi', 'wwii', 'medieval']

        for theme in themes:
            set_theme(theme)

        browser.close()

if __name__ == "__main__":
    verify_themes()
