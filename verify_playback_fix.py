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
        await page.goto('http://127.0.0.1:8000/products/player/0-01/')

        # Wait for the radio buttons to be rendered
        await page.wait_for_selector('#radiosL1 input[type="radio"]')

        # Select languages
        await page.click('#radiosL1 input[value="CA"]')
        await page.click('#radiosL2 input[value="EN"]')

        # Wait for the mode buttons to appear
        await page.wait_for_selector('#modeButtons button')

        # Click the 'CA-EN' mode button
        await page.click('#modeButtons button[data-mode="CA-EN"]')

        # Wait for the audio source to be set
        await page.wait_for_function("document.querySelector('#audio').src.includes('/static/AUDIOS/A0/0-01/CA/0-01-CA-001.mp3')")

        # Get the audio source
        audio_src = await page.get_attribute('#audio', 'src')

        if '/static/AUDIOS/A0/0-01/CA/0-01-CA-001.mp3' in audio_src:
            print("Test passed: The correct audio file is being played.")
        else:
            print(f"Test failed: The audio source is incorrect. Expected to find '/static/AUDIOS/A0/0-01/CA/0-01-CA-001.mp3' but got '{audio_src}' instead.")

        # Create the verification directory if it doesn't exist
        verification_dir = Path('/home/jules/verification')
        verification_dir.mkdir(exist_ok=True)

        # Capture a screenshot
        screenshot_path = verification_dir / 'playback_verification_fix.png'
        await page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
