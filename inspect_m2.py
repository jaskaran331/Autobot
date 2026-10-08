from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=100)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)

    # Click Semester 1
    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Look for Milestone 2
    # In the Milestones list, find the card with "Milestone 2" and click its Continue Learning
    print("Finding Milestone 2...")
    m2_btn = None
    cards = page.query_selector_all('div:has-text("Milestone 2")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            m2_btn = btn
            break

    if not m2_btn:
        # Fallback: get all continue learning buttons
        all_btns = page.query_selector_all('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if len(all_btns) >= 2:
            m2_btn = all_btns[1]

    if m2_btn:
        print("Clicking Milestone 2 button...")
        m2_btn.click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')

        print("Current URL:", page.url)
        page.screenshot(path='generated/m2_tasks.png', full_page=True)

        print("\n=== MILESTONE 2 HEADINGS ===")
        for h in page.query_selector_all('h1, h2, h3, h4, h5'):
            t = (h.inner_text() or "").strip()
            if t:
                print(f"  {h.evaluate('e => e.tagName')}: {t}")

        print("\n=== MILESTONE 2 BUTTONS ===")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

    browser.close()
