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
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Quiz button on left
    quiz_btn = page.query_selector('button:has-text("quiz"), button:has-text("Quiz")')
    if quiz_btn:
        print("Found quiz button:", quiz_btn.inner_text().replace('\n', ' '))
        quiz_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        page.screenshot(path='generated/m3_t1_quiz_view.png', full_page=True)

        print("\n=== RIGHT PANEL / QUIZ HTML FRAGMENT ===")
        # Find quiz form or right panel
        right_panel = page.query_selector('div.flex-1.min-w-0, form, div:has-text("Quiz")')
        if right_panel:
            print("Right panel text:\n", right_panel.inner_text())

        # Inspect all options / radio buttons / labels / buttons in quiz
        print("\n=== QUIZ INTERACTIVE ELEMENTS ===")
        for el in page.query_selector_all('input, label, button, [role="radio"], [role="checkbox"]'):
            typ = el.get_attribute('type') or el.evaluate('e => e.tagName')
            role = el.get_attribute('role')
            val = el.get_attribute('value') or ''
            txt = el.inner_text().strip().replace('\n', ' ')
            if txt or typ == 'radio':
                print(f"  [{typ}] role={role} val={val}: {txt[:80]}")

    browser.close()
