import time
from playwright.sync_api import sync_playwright, expect

def verify_kanban_board(page):
    # Wait for Vite to start
    time.sleep(3)

    print("Navigating to root...")
    # Since I modified App.jsx to make ProjectManagement the root, this should work
    page.goto("http://localhost:5173/", timeout=10000)

    print("Waiting for columns...")
    # Check for column headers
    expect(page.get_by_text("待办")).to_be_visible(timeout=20000)
    expect(page.get_by_text("翻译中")).to_be_visible()
    expect(page.get_by_text("校对中")).to_be_visible()

    print("Columns found. Waiting for tasks...")
    # Check for a known task from mock data
    expect(page.get_by_text("events_l_english.yml")).to_be_visible()
    expect(page.get_by_text("Fix typo in intro")).to_be_visible()

    print("Tasks found. Taking initial screenshot...")
    page.screenshot(path="verification/kanban_initial.png", full_page=True)

    print("Testing interaction: Click a task...")
    # Click the "Fix typo in intro" task
    page.get_by_text("Fix typo in intro").click()

    print("Waiting for sidebar...")
    # Verify sidebar content appears
    expect(page.get_by_text("Comments & Notes")).to_be_visible()

    # Fallback to get_by_role or input locator if get_by_display_value is not available or flaky
    # The title input should contain the text
    expect(page.locator("input[value='Fix typo in intro']")).to_be_visible()

    print("Sidebar verified. Taking interaction screenshot...")
    page.screenshot(path="verification/kanban_sidebar.png", full_page=True)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        try:
            verify_kanban_board(page)
            print("Verification successful!")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/failure.png")
        finally:
            browser.close()
