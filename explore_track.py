from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    btns = page.query_selector_all('button')
    start_btns = [b for b in btns if "start learning" in (b.inner_text() or "").lower()]
    print(f"Found {len(start_btns)} Start Learning buttons")

    if start_btns:
        print("Clicking first Start Learning button...")
        start_btns[0].click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')
        print("New URL:", page.url)
        page.screenshot(path='generated/semester_view.png', full_page=True)

        # List all clickable items, modules, lessons on this semester view
        print("\nAll links on semester view:")
        for link in page.query_selector_all('a[href]'):
            t = (link.inner_text() or "").strip().replace('\n', ' ')
            h = link.get_attribute('href') or ""
            if t or h:
                print(f"  {t} -> {h}")

        print("\nAll buttons on semester view:")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

    browser.close()
