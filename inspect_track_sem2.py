import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)
    
    # Scroll down 600px to bring Semester 2 into full view
    page.mouse.wheel(0, 600)
    time.sleep(1)
    page.screenshot(path='artifacts/sem2_in_view.png', full_page=False)
    
    # Find all buttons in Semester 2
    sem2_card = page.locator('div:has-text("Semester 2")')
    print("Semester 2 card count:", sem2_card.count())
    
    btns = page.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    print("All start/continue buttons count:", btns.count())
    for i in range(btns.count()):
        b = btns.nth(i)
        print(f"Btn {i}: visible={b.is_visible()} text={b.inner_text()}")
        
    browser.close()
