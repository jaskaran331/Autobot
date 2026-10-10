from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)
    print('Current URL:', page.url)
    
    # Expand Semester 2
    sem_btns = page.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    print('Sem buttons count:', sem_btns.count())
    if sem_btns.count() >= 2:
        print('Clicking Semester 2 button...')
        sem_btns.nth(1).click()
        time.sleep(2)
    
    # Scroll down to Milestone 11
    for _ in range(5):
        page.mouse.wheel(0, 1500)
        time.sleep(0.3)
    
    # Find Milestone 11 button
    m11 = page.locator('text=Milestone 11').first
    if m11.count():
        print('Milestone 11 visible!')
        # Look for buttons near Milestone 11
        parent = m11.locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "rounded") or contains(@class, "border")][1]')
        if parent.count():
            btn = parent.locator('button')
            print('Parent button:', btn.all_inner_texts())
            btn.first.click()
        else:
            m11.click()
    else:
        print('Milestone 11 text not found!')

    time.sleep(3)
    page.screenshot(path='artifacts/m11_inside.png', full_page=True)
    browser.close()
