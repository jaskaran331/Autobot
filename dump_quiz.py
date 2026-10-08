from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')

    # Semester 1
    btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if btns:
        btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Milestone 1
    continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
    if continue_btns:
        continue_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Task 3
    task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if len(task_btns) >= 2:
        task_btns[1].click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')

    # Click Quiz
    quiz_btns = [b for b in page.query_selector_all('button') if "quiz" in (b.inner_text() or "").lower()]
    if quiz_btns:
        quiz_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Dump right panel text
        print("=== QUIZ QUESTIONS AND OPTIONS ===")
        # Look for all question texts and option items
        questions = page.query_selector_all('[class*="quiz"], form, div')
        full_text = page.inner_text('body')
        # Print lines after "Attempt task 03 quiz"
        if "Attempt task 03 quiz" in full_text:
            part = full_text.split("Attempt task 03 quiz", 1)[1]
            if "Submit Quiz" in part:
                part = part.split("Submit Quiz", 1)[0]
            print(part.strip())

    browser.close()
