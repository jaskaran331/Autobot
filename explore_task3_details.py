from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    # Go to track
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')

    # Click Semester 1 Start Learning
    btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if btns:
        btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Milestone 1 Continue Learning
    continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
    if continue_btns:
        continue_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Task 3
    task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if len(task_btns) >= 2:
        task_btns[1].click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')

    # Now click the second sub-item: "Talk to 2 sellers in your area"
    sub_btns = [b for b in page.query_selector_all('button') if "talk to 2 sellers" in (b.inner_text() or "").lower()]
    print(f"Found 'talk to 2 sellers' button: {len(sub_btns)}")
    if sub_btns:
        sub_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        page.screenshot(path='generated/task_3_seller_assignment.png', full_page=True)

        print("\nAll inputs / textareas / buttons on right panel:")
        for inp in page.query_selector_all('input, textarea, select'):
            typ = inp.get_attribute('type') or inp.evaluate('e => e.tagName')
            ph = inp.get_attribute('placeholder') or inp.get_attribute('name') or ''
            print(f"  Input [{typ}]: {ph}")

        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

    # Now also click the third sub-item: "Attempt task 03 quiz"
    quiz_btns = [b for b in page.query_selector_all('button') if "quiz" in (b.inner_text() or "").lower()]
    print(f"\nFound quiz button: {len(quiz_btns)}")
    if quiz_btns:
        quiz_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        page.screenshot(path='generated/task_3_quiz.png', full_page=True)

    browser.close()
