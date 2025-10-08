from playwright.sync_api import sync_playwright, Page, expect

def verify_glossary_manager(page: Page):
    """
    Navigates to the Glossary Manager page, filters the table,
    and takes a screenshot demonstrating the key features.
    """
    # 1. Navigate to the Glossary Manager page
    page.goto("http://localhost:5173/glossary-manager")

    # 2. Wait for the game selection dropdown to ensure the page has loaded.
    expect(page.locator('.ant-select-selector')).to_be_visible()
    print("Page loaded, game selector is visible.")

    # 3. Find the filter input and type text into it.
    filter_input = page.get_by_placeholder("Filter content...")
    filter_input.fill("gdp")
    print("Filtered the table with 'gdp'.")

    # 4. Verify that the table has been filtered to one row.
    expect(page.locator('table tbody tr')).to_have_count(1)
    print("Table filtered successfully, 1 row found.")

    # 5. Use the robust data-testid to locate and double-click the cell's div.
    # The ID for the 'gdp' row is 'v3_eco_001' and the column is 'translation'.
    cell_div_locator = page.locator('[data-testid="cell-v3_eco_001-translation"]')
    expect(cell_div_locator).to_be_visible()
    cell_div_locator.dblclick()

    # 6. After the double-click, the div is replaced by an input.
    # We now expect an input element to be visible within the parent <td> of the div.
    # We locate the parent `td` that contains our specific `div` and then find the input inside it.
    parent_td_locator = page.locator('td:has([data-testid="cell-v3_eco_001-translation"])')
    expect(parent_td_locator.locator('input')).to_be_visible(timeout=5000) # Increased timeout for react re-render
    print("Cell put into edit mode, input is visible.")

    # 7. Take a screenshot to visually verify the feature.
    screenshot_path = "jules-scratch/verification/verification.png"
    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")


# --- Boilerplate to run the script ---
with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=True)
    except Exception:
        print("Chromium not found. Installing...")
        from playwright.sync_api import Error
        try:
            p.chromium.install()
            browser = p.chromium.launch(headless=True)
        except Error as e:
            print(f"Failed to install or launch Chromium: {e}")
            exit(1)

    page = browser.new_page()
    try:
        verify_glossary_manager(page)
        print("Verification script completed successfully.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")
        error_screenshot_path = "jules-scratch/verification/error.png"
        page.screenshot(path=error_screenshot_path)
        print(f"Error screenshot saved to {error_screenshot_path}")
    finally:
        browser.close()
