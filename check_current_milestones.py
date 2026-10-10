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
    print('Clicking Semester 2 button...')
    sem_btns.nth(1).scroll_into_view_if_needed()
    sem_btns.nth(1).click()
    time.sleep(2)
    
    # Scroll down to milestones
    for _ in range(5):
        page.mouse.wheel(0, 1500)
        time.sleep(0.2)
        
    page.screenshot(path='artifacts/current_milestones.png', full_page=True)
    for m in [10, 11, 12, 13]:
        card = page.locator(f'text="Milestone {m}"')
        print(f'Milestone {m} found: {card.count()}, visible: {card.first.is_visible() if card.count() else False}')
    browser.close()
