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

    # Look for Task 3 Start Learning button
    all_btns = page.query_selector_all('button')
    task_btns = [b for b in all_btns if "start learning" in (b.inner_text() or "").lower()]
    print(f"Task Start Learning buttons: {len(task_btns)}")

    # We want Task 3 (the second uncompleted task in Milestone 1)
    if len(task_btns) >= 2:
        print("Clicking Task 3 Start Learning...")
        task_btns[1].click()
        time.sleep(4)
        page.wait_for_load_state('networkidle')
        print("Task 3 URL:", page.url)
        page.screenshot(path='generated/task_3_view.png', full_page=True)

        with open('generated/task_3.html', 'w', encoding='utf-8') as f:
            f.write(page.content())

        print("\nTask 3 Buttons / Sub-items:")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

        print("\nTask 3 Inputs:")
        for inp in page.query_selector_all('input, textarea, select'):
            typ = inp.get_attribute('type') or inp.evaluate('e => e.tagName')
            ph = inp.get_attribute('placeholder') or inp.get_attribute('name') or ''
            print(f"  Input [{typ}]: {ph}")

    browser.close()
