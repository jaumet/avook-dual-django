
import re
from playwright.sync_api import sync_playwright, expect
import os

def run(playwright):
    # Create verification directory if it doesn't exist
    os.makedirs("verification", exist_ok=True)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(locale="ca-ES")
    page = context.new_page()

    try:
        # Log in
        page.goto("http://localhost:8000/ca/accounts/login/")
        page.get_by_label("Username:").fill("admin")
        page.get_by_label("Password:").fill("password")
        page.get_by_role("button", name="Inicia sessió").click()

        # Go to the product tests page
        page.goto("http://localhost:8000/ca/products/Dual-Free-Test/tests/")

        # 1. Verify page content and take screenshot
        expect(page.get_by_text("Tests for Dual Free Test")).to_be_visible()

        # Explicitly check for a title that SHOULD be on the page
        expect(page.get_by_text("Un petit test")).to_be_visible()

        # Explicitly check for a title that SHOULD NOT be on the page
        expect(page.get_by_text("Some Other Title")).not_to_be_visible()

        page.screenshot(path="verification/correct_titles.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
