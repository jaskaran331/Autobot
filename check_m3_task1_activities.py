from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
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

    # Task 1
    task_btns = page.query_selector_all('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    print("Inside M3 Task 1:")
    # List all activity buttons/items
    items = page.query_selector_all('button, div[role="button"]')
    for i in items:
        txt = i.inner_text().strip().replace('\n', ' | ')
        if any(w in txt for w in ["video", "supplier", "suppliers", "quiz", "Quiz", "Search"]):
            print("  Item:", txt)
            
    page.screenshot(path='generated/m3_task1_inside.png', full_page=True)
    browser.close()
