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

    page.screenshot(path='generated/sem1_after_m2.png', full_page=True)

    # Check status of Milestone 2 and Milestone 3 cards
    print("=== MILESTONE CARDS ===")
    cards = page.query_selector_all('div')
    for c in page.query_selector_all('div:has-text("Milestone")'):
        t = c.inner_text().strip()
        if "Milestone" in t and len(t) < 200:
            print("  Card:", t.replace('\n', ' | '))

    # Look for Milestone 3 button
    cards_m3 = page.query_selector_all('div:has-text("Milestone 3")')
    m3_btn = None
    for c in cards_m3:
        btn = c.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if btn:
            m3_btn = btn
            break

    if m3_btn:
        print("\nClicking Milestone 3 button:", m3_btn.inner_text())
        m3_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        page.screenshot(path='generated/m3_tasks.png', full_page=True)

        print("\nButtons inside Milestone 3:")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

        print("\nHeadings inside Milestone 3:")
        for h in page.query_selector_all('h1, h2, h3, h4, h5, h6'):
            t = (h.inner_text() or "").strip()
            if t:
                print(f"  {h.evaluate('e => e.tagName')}: {t}")
    else:
        print("\nMilestone 3 button NOT found directly. Let's inspect all buttons on milestones page:")
        for b in page.query_selector_all('button'):
            print("  Button:", b.inner_text().replace('\n', ' '))

    browser.close()
