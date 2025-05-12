# playwright_amazon_script.py

"""
This script is used to test the playwright captcha solver independently.
"""

from playwright.sync_api import sync_playwright
from playwright_captcha_solver import PlaywrightCaptchaSolver

# example for playwright captcha solver independently
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Amazon captcha page
            page.goto(
                "https://www.amazon.com/errors/validateCaptcha",
                wait_until="domcontentloaded"
            )

            # init CAPTCHA solver w/ debug output
            solver = PlaywrightCaptchaSolver(
                output_dir="captcha_output",
                save_debug_output=True
            )

            if not solver.solve_captcha(page):
                print("Failed to solve CAPTCHA")
                return

            # left captcha page, wait for home page
            page.wait_for_url(lambda url: "validateCaptcha" not in url,
                              timeout=15_000)
            page.wait_for_selector("#nav-logo-sprites", timeout=10_000)

            print("CAPTCHA solved")

        finally:
            browser.close()

if __name__ == "__main__":
    run()
