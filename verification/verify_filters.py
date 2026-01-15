
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
        page.goto("http://localhost:8000/ca/products/dual-progress/tests/")

        # 1. Verify initial state and take screenshot
        expect(page.get_by_text("Tests for Dual Progress")).to_be_visible()
        expect(page.locator(".level-container.A2")).to_be_visible()
        expect(page.locator(".level-container.B1")).to_be_visible()
        page.screenshot(path="verification/filters_before.png")

        # 2. Uncheck the 'A2' filter
        page.get_by_label("A2").uncheck()

        # 3. Verify that A2 titles are hidden and B1 are visible
        expect(page.locator(".level-container.A2")).not_to_be_visible()
        expect(page.locator(".level-container.B1")).to_be_visible()
        page.screenshot(path="verification/filters_after.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
