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

    # Click Milestone 2
    cards = page.query_selector_all('div:has-text("Milestone 2")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Click Task 1 in Milestone 2
    task1_btn = page.query_selector('button:has-text("Start Learning")')
    if task1_btn:
        task1_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Attempt task 01 quiz
    quiz_btn = page.query_selector('button:has-text("Attempt task 01 quiz")')
    if quiz_btn:
        quiz_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("=== M2 TASK 1 QUIZ TEXT ===")
        print(page.inner_text('body'))

    browser.close()
