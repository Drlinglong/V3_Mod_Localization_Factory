import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            # 1. Navigate and go to the translation page
            await page.goto("http://localhost:5173/")
            await page.get_by_role("menuitem", name="Translation").click()
            await expect(page.get_by_text("Upload Mod", exact=True)).to_be_visible()

            # 2. Upload a file to get to the configure step
            async with page.expect_file_chooser() as fc_info:
                await page.locator('.ant-upload-drag-icon').click()
            file_chooser = await fc_info.value
            await file_chooser.set_files('jules-scratch/verification/dummy.zip')

            # 3. Wait for the configure step to be visible and open a dropdown
            await expect(page.get_by_label("Game")).to_be_visible()
            await page.get_by_label("Game").click()

            # 4. Wait for an option to be visible to confirm data is loaded
            await expect(page.get_by_text("Victoria 3")).to_be_visible()

            # 5. Take the screenshot
            await page.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot captured successfully, dropdowns are populated.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
