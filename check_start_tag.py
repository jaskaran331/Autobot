from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    sem_btns = page.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    sem_btns.nth(1).scroll_into_view_if_needed()
    sem_btns.nth(1).click()
    page.wait_for_timeout(2000)
    for _ in range(5):
        page.mouse.wheel(0, 1500)
    m11 = page.locator('div:has-text("Milestone 11") button:has-text("Continue Learning")').first
    m11.click()
    page.wait_for_timeout(3000)
    
    starts = page.locator('text="Start Learning"')
    print('Start Learning count:', starts.count())
    for i in range(starts.count()):
        el = starts.nth(i)
        tag = el.evaluate('e => e.tagName')
        parent_tag = el.evaluate('e => e.parentElement.tagName')
        print(f'Item {i}: tag={tag}, parent={parent_tag}, visible={el.is_visible()}')
    browser.close()
