import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avook_site.settings')
import django
django.setup()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Capture console messages
        page.on('console', lambda msg: print(f"Browser console: {msg.text}"))

        # Navigate to the player page
        await page.goto('http://127.0.0.1:8000/products/player/Test-1/')

        # Wait for the radio buttons to be rendered by the JavaScript
        await page.wait_for_selector('#radiosL1 input[type="radio"]')
        await page.wait_for_selector('#radiosL2 input[type="radio"]')

        # Select the first language (e.g., 'CA')
        await page.click('#radiosL1 input[value="CA"]')

        # Check if the same language is disabled in the second selector
        is_disabled = await page.is_disabled('#radiosL2 input[value="CA"]')

        if is_disabled:
            print("Test passed: Selecting 'CA' in the first selector disables it in the second.")
        else:
            print("Test failed: Selecting 'CA' in the first selector did not disable it in the second.")

        # Create the verification directory if it doesn't exist
        verification_dir = Path('/home/jules/verification')
        verification_dir.mkdir(exist_ok=True)

        # Capture a screenshot
        screenshot_path = verification_dir / 'language_selectors.png'
        await page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
