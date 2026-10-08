from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
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

    # Open Milestone 2
    cards = page.query_selector_all('div:has-text("Milestone 2")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Open Task 2 in Milestone 2
    task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Quiz
    quiz_btn = page.query_selector('button:has-text("Attempt task 02 quiz")')
    if quiz_btn:
        quiz_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("=== M2 TASK 2 QUIZ TEXT ===")
        print(page.inner_text('body'))

    browser.close()
