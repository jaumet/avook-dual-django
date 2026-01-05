from playwright.sync_api import sync_playwright
import os

def run(playwright):
    # Create verification directory if it doesn't exist
    os.makedirs("verification", exist_ok=True)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Go to the English login page
        page.goto("http://127.0.0.1:8000/en/accounts/login/")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin")
        page.click("button[type='submit']")

        # Wait for the English home page
        page.wait_for_url("http://127.0.0.1:8000/en/", timeout=60000)

        # Go to the product detail page
        page.goto("http://127.0.0.1:8000/en/products/product/13/")

        # Take a screenshot to verify
        page.screenshot(path="verification/product_detail_fixed.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
