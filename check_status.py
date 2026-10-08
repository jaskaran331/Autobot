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
    time.sleep(2)
    print("Track URL:", page.url)
    page.screenshot(path='generated/current_track.png', full_page=True)

    # Click Semester 1
    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        print("Semester button text:", sem_btn.inner_text())
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        print("After semester click URL:", page.url)
        page.screenshot(path='generated/current_sem1.png', full_page=True)

    # Check all milestones listed
    print("\nMilestones on page:")
    cards = page.query_selector_all('div')
    for card in page.query_selector_all('div:has-text("Milestone")'):
        text = card.inner_text().strip()
        # only print top level summary
        if "Milestone" in text and len(text) < 200:
            print("  Card:", text.replace('\n', ' | '))

    browser.close()
