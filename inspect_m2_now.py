from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=100)
    except Exception:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)

    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Find Milestone 2 card button
    cards = page.query_selector_all('div:has-text("Milestone 2")')
    m2_btn = None
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            m2_btn = btn
            break
    if m2_btn:
        m2_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    print("Milestone 2 page URL:", page.url)
    page.screenshot(path='generated/m2_tasks_now.png', full_page=True)

    # Print all tasks cards/buttons
    print("\nButtons on Milestone 2 page:")
    for b in page.query_selector_all('button'):
        t = (b.inner_text() or "").strip().replace('\n', ' ')
        if t:
            print(f"  Button: {t}")

    # Check tasks listed
    print("\nHeadings:")
    for h in page.query_selector_all('h1, h2, h3, h4, h5, h6, [class*="title"], [class*="task"]'):
        t = (h.inner_text() or "").strip().replace('\n', ' ')
        if t and len(t) < 150:
            print(f"  {h.evaluate('e => e.tagName')}: {t}")

    browser.close()
