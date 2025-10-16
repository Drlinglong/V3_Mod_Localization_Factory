from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the app
            page.goto("http://localhost:5178", timeout=60000)

            # 2. Check the title
            expect(page).to_have_title("Smart Localization Workbench v2.0")
            page.pause()
            # 3. Click the Burger menu to open the navbar on mobile
            burger = page.get_by_label("Open navigation")
            expect(burger).to_be_visible()
            burger.click()

            # 4. Click the 'Translation' link in the AppShell navbar
            translation_link = page.get_by_role("a", name="Translation")
            expect(translation_link).to_be_visible()
            translation_link.click()

            # 5. Verify the new page content is loaded
            project_path_input = page.get_by_label("Project Source Path")
            expect(project_path_input).to_be_visible()

            # 6. Take a screenshot
            page.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot taken successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Save a screenshot on error for debugging
            page.screenshot(path="jules-scratch/verification/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
