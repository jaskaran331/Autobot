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

    print("URL:", page.url)
    tasks = page.query_selector_all('div[class*="rounded"], div[class*="card"]')
    for t in tasks:
        txt = t.inner_text().strip().replace('\n', ' | ')
        if "Task" in txt and len(txt) < 300:
            print("TASK:", txt)
    
    browser.close()
