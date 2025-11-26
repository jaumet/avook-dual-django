from playwright.sync_api import sync_playwright
import os
import time

def run(playwright):
    # Create verification directory if it doesn't exist
    os.makedirs("verification", exist_ok=True)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Listen for console messages
    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

    try:
        # Log in
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin")
        page.click("button[type='submit']")
        page.wait_for_url("http://127.0.0.1:8000/", timeout=60000)

        # Go to the catalog page
        page.goto("http://127.0.0.1:8000/")

        # Take a screenshot before applying filters
        page.screenshot(path="verification/catalog_before_filter.png")

        # Wait for the level buttons to appear
        page.wait_for_selector("button.levelBtn:has-text('A1')", timeout=10000)

        # Apply a level filter
        page.click("button.levelBtn:has-text('A1')")

        # Add a small delay to see the filtering effect
        time.sleep(1)

        # Take a screenshot after applying the filter
        page.screenshot(path="verification/catalog_after_filter.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
