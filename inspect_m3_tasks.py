from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=50)
    except Exception:
        browser = pw.chromium.launch(headless=False, slow_mo=50)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(1)

    # Click Semester 1
    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Milestone 3
    cards = page.query_selector_all('div:has-text("Milestone 3")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Click first Start Learning (Task 1)
    task_btns = page.query_selector_all('button:has-text("Start Learning")')
    print(f"Found {len(task_btns)} task Start Learning buttons")
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("\n=== INSIDE M3 TASK 1 ===")
        page.screenshot(path='generated/m3_task1.png', full_page=True)

        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

        for h in page.query_selector_all('h1, h2, h3, h4, h5, h6'):
            t = (h.inner_text() or "").strip()
            if t:
                print(f"  {h.evaluate('e => e.tagName')}: {t}")

    browser.close()
