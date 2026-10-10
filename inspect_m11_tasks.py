import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)
    
    # Click Semester 2 button
    sem_btns = page.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    sem_btns.nth(1).scroll_into_view_if_needed()
    sem_btns.nth(1).click()
    time.sleep(2)
    
    # Scroll down to milestones
    for _ in range(5):
        page.mouse.wheel(0, 1500)
        time.sleep(0.2)
        
    m11_btn = page.locator('div:has-text("Milestone 11") button:has-text("Continue Learning"), div:has-text("Milestone 11") button:has-text("Start Learning")').first
    m11_btn.scroll_into_view_if_needed()
    m11_btn.click()
    time.sleep(3)
    
    page.screenshot(path='artifacts/m11_tasks_now.png', full_page=True)
    print("Tasks text:")
    for t in page.locator('div:has-text("Task ")').all():
        print("---", t.inner_text()[:80].replace("\n", " "))
    browser.close()
