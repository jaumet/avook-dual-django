import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to product list (logged out)
        await page.goto('http://localhost:8000/ca/products/')
        await page.wait_for_timeout(2000)

        await page.screenshot(path='/home/jules/verification/logged_out.png', full_page=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
