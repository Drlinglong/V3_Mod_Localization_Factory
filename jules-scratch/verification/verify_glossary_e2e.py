from playwright.sync_api import sync_playwright, Page, expect
import time

def verify_glossary_e2e(page: Page):
    """
    Performs an end-to-end test of the Glossary Manager, verifying
    API connections and the full CRUD flow. This final version uses a
    highly specific chained locator to select the correct file.
    """
    # 1. Navigate to the page
    page.goto("http://localhost:5173/glossary-manager")
    print("Navigated to the Glossary Manager page.")

    # 2. Wait for the tree to be populated
    expect(page.get_by_text("glossary.json")).to_be_visible(timeout=10000)
    print("File tree loaded successfully.")

    # 3. Use a chained locator to select the correct 'glossary.json'
    # First, find the parent tree node for 'victoria3'
    # Ant Design tree nodes with children have a specific structure we can target.
    victoria3_node = page.locator(".ant-tree-treenode-switcher-open").filter(has_text="victoria3")

    # Then, find the 'glossary.json' link specifically within that node's context.
    file_to_select = victoria3_node.locator("..").locator("..").get_by_text("glossary.json")

    expect(file_to_select).to_be_visible()
    file_to_select.click()
    print("Clicked on 'victoria3/glossary.json'.")

    # 4. Wait for the correct table content to load
    expect(page.get_by_text("美利坚")).to_be_visible(timeout=10000)
    print("Table content for victoria3 loaded successfully.")

    # 5. Click the 'Add New Entry' button
    add_button = page.get_by_role("button", name="新增词条")
    expect(add_button).to_be_enabled()
    add_button.click()
    print("Clicked 'Add New Entry' button.")

    # 6. Fill out the modal form
    modal = page.get_by_role("dialog", name="新增词条")
    source_text = f"test_source_{int(time.time())}"
    translation_text = "测试译文"
    modal.get_by_label("原文").fill(source_text)
    modal.get_by_label("译文 (简体中文)").fill(translation_text)
    modal.get_by_label("备注").fill("This is a test entry.")
    print("Filled out the form.")

    # 7. Submit the form
    modal.get_by_role("button", name="OK").click()
    print("Form submitted.")

    # 8. Verify the new entry appears in the table
    expect(page.get_by_text(source_text)).to_be_visible(timeout=10000)
    print("New entry successfully found in the table.")

    # 9. Take the final screenshot
    screenshot_path = "jules-scratch/verification/verification_e2e.png"
    page.screenshot(path=screenshot_path)
    print(f"E2E verification screenshot saved to {screenshot_path}")

# --- Boilerplate ---
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        verify_glossary_e2e(page)
        print("E2E verification script completed successfully.")
    except Exception as e:
        print(f"An error occurred during E2E verification: {e}")
        page.screenshot(path="jules-scratch/verification/error_e2e.png")
    finally:
        browser.close()
