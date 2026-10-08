import time
from playwright.sync_api import sync_playwright

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

    # Click Quiz item
    quiz_card = page.query_selector('div:has-text("Attempt task 01 quiz"), button:has-text("Attempt task 01 quiz")')
    if quiz_card:
        quiz_card.click()
        time.sleep(1.5)
        st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
        if st and st.is_visible():
            st.click()
            time.sleep(2)

    # Answers:
    # 1. Product quality and delivery time
    # 2. IndiaMART
    # 3. Visit their store or warehouse
    # 4. Check prices, samples, and terms
    # 5. Visit local wholesale markets
    answers = [
        "Product quality and delivery time",
        "IndiaMART",
        "Visit their store or warehouse",
        "Check prices, samples, and terms",
        "Visit local wholesale markets"
    ]
    
    # We can select buttons or radio labels
    for ans in answers:
        btns = page.query_selector_all('button, label, div[role="radio"]')
        for b in btns:
            txt = b.inner_text().strip()
            if ans in txt and b.is_visible():
                b.click()
                print(f"Selected: {ans}")
                time.sleep(0.5)
                break

    sub_quiz = page.query_selector('button:has-text("Submit Quiz")')
    if sub_quiz and sub_quiz.is_visible():
        sub_quiz.click()
        print("Clicked Submit Quiz!")
        time.sleep(3)

    page.screenshot(path='generated/m3_task1_quiz_done.png', full_page=True)
    browser.close()
