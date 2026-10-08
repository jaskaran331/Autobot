from playwright.sync_api import sync_playwright
import time

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    # Go to track and open Semester 1
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    btns = page.query_selector_all('button')
    start_btns = [b for b in btns if "start learning" in (b.inner_text() or "").lower()]
    if start_btns:
        start_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Now on Milestones list, click Continue Learning on Milestone 1
    continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
    print(f"Found {len(continue_btns)} Continue Learning buttons")
    if continue_btns:
        print("Clicking Milestone 1 Continue Learning...")
        continue_btns[0].click()
        time.sleep(3)
        page.wait_for_load_state('networkidle')
        print("Milestone 1 URL:", page.url)
        page.screenshot(path='generated/milestone_1_tasks.png', full_page=True)

        # Dump text and HTML
        with open('generated/milestone_1.html', 'w', encoding='utf-8') as f:
            f.write(page.content())

        # Inspect elements
        print("\nPage Title/Headings:")
        for h in page.query_selector_all('h1, h2, h3, h4, [class*="title"]'):
            t = (h.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  {h.evaluate('e => e.tagName')}: {t}")

        print("\nAll buttons:")
        for b in page.query_selector_all('button'):
            t = (b.inner_text() or "").strip().replace('\n', ' ')
            if t:
                print(f"  Button: {t}")

        print("\nAll inputs / textareas / files:")
        for inp in page.query_selector_all('input, textarea, select'):
            typ = inp.get_attribute('type') or inp.evaluate('e => e.tagName')
            name = inp.get_attribute('name') or inp.get_attribute('placeholder') or ''
            print(f"  Input [{typ}]: {name}")

    browser.close()
