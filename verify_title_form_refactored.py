from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Wait for the server to start
        time.sleep(5)

        # Log in
        page.goto("http://127.0.0.1:8000/accounts/login/")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin")
        page.click("button[type='submit']")
        page.wait_for_url("http://127.0.0.1:8000/", timeout=60000)

        # Go to the add title page
        page.goto("http://127.0.0.1:8000/products/title/add/")

        # Take a screenshot before clicking the button
        page.screenshot(path="/home/jules/verification/title_form_refactored_before.png")

        # Click the "Nova llengua" button
        page.click("#add-language-form")

        # Take a screenshot after clicking the button
        page.screenshot(path="/home/jules/verification/title_form_refactored_after.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="/home/jules/verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
