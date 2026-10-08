from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=100)
    except Exception:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(1)

    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    cards = page.query_selector_all('div:has-text("Milestone 2")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Click Start Learning on Task 3
    task_btn = page.query_selector('button:has-text("Start Learning")')
    if task_btn:
        task_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    print("Task 3 page URL:", page.url)
    page.screenshot(path='generated/m2_task3_inside.png', full_page=True)

    print("\nButtons inside Task 3:")
    for b in page.query_selector_all('button'):
        t = (b.inner_text() or "").strip().replace('\n', ' ')
        if t:
            print(f"  Button: {t}")

    print("\nHeadings inside Task 3:")
    for h in page.query_selector_all('h1, h2, h3, h4, h5, h6'):
        t = (h.inner_text() or "").strip()
        if t:
            print(f"  {h.evaluate('e => e.tagName')}: {t}")

    browser.close()
