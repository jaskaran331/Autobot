from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)

    # Click Semester 1 button
    sem1 = page.wait_for_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem1:
        sem1.click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')

    page.screenshot(path='generated/all_milestones_updated.png', full_page=True)

    # List all milestone cards and their text
    for card in page.query_selector_all('[class*="card"], div:has-text("Milestone")'):
        t = (card.inner_text() or "").strip().replace('\n', ' ')
        if "Milestone" in t and len(t) < 150:
            print("Card:", t)

    browser.close()
