from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')

    btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if btns:
        btns[0].click()
        time.sleep(2)

    continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
    if continue_btns:
        continue_btns[0].click()
        time.sleep(2)

    task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
    if len(task_btns) >= 2:
        task_btns[1].click()
        time.sleep(3)

    quiz_btns = [b for b in page.query_selector_all('button') if "quiz" in (b.inner_text() or "").lower()]
    if quiz_btns:
        quiz_btns[0].click()
        time.sleep(2)

        # Scroll right pane
        right_panel = page.query_selector('div:has-text("Attempt task 03 quiz")')
        if right_panel:
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        page.screenshot(path='generated/quiz_scrolled.png', full_page=True)

        # Extract all text from the quiz panel
        print(page.inner_text('div:has-text("Attempt task 03 quiz")'))

    browser.close()
