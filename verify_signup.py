from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:8000/accounts/signup/")

    page.fill('input[name="username"]', "testuser")
    page.fill('input[name="email"]', "test@example.com")
    page.fill('input[name="password1"]', "testpassword")
    page.fill('input[name="password2"]', "testpassword")
    page.click('button[type="submit"]')

    expect(page.locator("text=Compte creat! Ja pots iniciar sessió.")).to_be_visible()

    page.screenshot(path="verification/signup_success.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
