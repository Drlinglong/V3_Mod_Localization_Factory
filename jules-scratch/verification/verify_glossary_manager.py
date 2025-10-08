from playwright.sync_api import sync_playwright, Page, expect

def verify_new_glossary_manager(page: Page):
    """
    Verifies the redesigned Glossary Manager page, including the
    two-column layout and the complete 'Add New Entry' CRUD flow.
    This final version uses a highly specific locator to avoid strict mode violations.
    """
    # 1. Navigate to the page
    page.goto("http://localhost:5173/glossary-manager")
    print("Navigated to the Glossary Manager page.")

    # 2. Verify the new two-column layout by checking for component roles
    expect(page.locator('.ant-select')).to_be_visible()
    expect(page.locator('.ant-tree')).to_be_visible()
    expect(page.get_by_role("table")).to_be_visible()
    print("Two-column layout verified by component presence.")

    # 3. CRITICAL FIX: Use a chained locator to select the file within the tree.
    tree_locator = page.locator(".ant-tree")
    file_to_select = tree_locator.get_by_text("glossary_art.yml")
    expect(file_to_select).to_be_visible()
    file_to_select.click()
    print("Clicked on 'glossary_art.yml' to select a file.")

    # 4. Find and click the 'Add New Entry' button.
    add_button = page.get_by_role("button", name=t('glossary_add_entry'))
    expect(add_button).to_be_enabled(timeout=5000)
    add_button.click()
    print("Clicked 'Add New Entry' button.")

    # 5. Verify the modal and its form appear.
    modal = page.get_by_role("dialog", name=t('glossary_add_entry'))
    expect(modal).to_be_visible()
    expect(modal.get_by_label(t('glossary_source_text'))).to_be_visible()
    print("Modal with form appeared.")

    # 6. Fill out the form
    modal.get_by_label(t('glossary_source_text')).fill("paradrop")
    modal.get_by_label(t('glossary_translation')).fill("空投")
    modal.get_by_label(t('glossary_notes')).fill("From a plane")
    modal.get_by_label(t('glossary_variants')).fill("伞降, 空降")
    print("Filled out the form.")

    # 7. Submit the form
    modal.get_by_role("button", name="OK").click()
    expect(modal).not_to_be_visible()
    print("Form submitted.")

    # 8. Verify the new entry is in the table.
    expect(page.locator('table tr:has-text("paradrop")')).to_be_visible()
    print("New entry found in the table.")

    # 9. Take a screenshot for visual verification
    screenshot_path = "jules-scratch/verification/verification.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

# --- A simple mock t function for the script to run ---
i18n_keys = {
    "glossary_add_entry": "Add New Entry",
    "glossary_edit_entry": "Edit Entry",
    "glossary_game": "Game",
    "glossary_files": "Glossary Files",
    "glossary_content": "Content",
    "glossary_source_text": "Source Text",
    "glossary_translation": "Translation",
    "glossary_notes": "Notes",
    "glossary_variants": "Variants"
}
def t(key):
    return i18n_keys.get(key, key)

# --- Boilerplate to run the script ---
with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=True)
    except Exception:
        print("Chromium not found, attempting to install...")
        from playwright.sync_api import Error
        import subprocess
        try:
            subprocess.run(["playwright", "install", "chromium"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
             print(f"Failed to install or launch Chromium: {e}")
             exit(1)
        browser = p.chromium.launch(headless=True)

    page = browser.new_page()
    try:
        verify_new_glossary_manager(page)
        print("Verification script completed successfully.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")
        error_screenshot_path = "jules-scratch/verification/error.png"
        page.screenshot(path=error_screenshot_path)
        print(f"Error screenshot saved to {error_screenshot_path}")
    finally:
        browser.close()
