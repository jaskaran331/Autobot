from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    # Go to track and open Semester 1
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    btns = page.query_selector_all('button')
    start_btns = [b for b in btns if "start learning" in (b.inner_text() or "").lower()]
    if start_btns:
        start_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Milestone 1 Continue Learning
    continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
    if continue_btns:
        continue_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Task 2 Start Learning
    task_start_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    print(f"Found {len(task_start_btns)} task Start Learning buttons")
    if task_start_btns:
        print("Clicking Task 2 Start Learning...")
        task_start_btns[0].click()
        time.sleep(4)
        page.wait_for_load_state('networkidle')
        print("Task 2 URL:", page.url)
        page.screenshot(path='generated/task_2_view.png', full_page=True)

        with open('generated/task_2.html', 'w', encoding='utf-8') as f:
            f.write(page.content())

        print("\nHeadings:")
        for h in page.query_selector_all('h1, h2, h3, h4, h5, p'):
            t = (h.inner_text() or "").strip().replace('\n', ' ')
            if t and len(t) < 100:
                print(f"  {h.evaluate('e => e.tagName')}: {t}")

        print("\nButtons:")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

        print("\nInputs:")
        for inp in page.query_selector_all('input, textarea, select'):
            typ = inp.get_attribute('type') or inp.evaluate('e => e.tagName')
            ph = inp.get_attribute('placeholder') or inp.get_attribute('name') or ''
            print(f"  Input [{typ}]: {ph}")

    browser.close()
