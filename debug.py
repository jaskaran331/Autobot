from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state='session.json')
    page = context.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track')
    page.wait_for_timeout(3000)
    
    starts = page.query_selector_all('button >> text="Start Learning"')
    for s in starts:
        if s.is_visible():
            try:
                parent = page.evaluate("(el) => { let p = el.closest('.bg-white'); return p ? p.innerText : ''; }", s)
                if 'Semester 1' in parent:
                    continue
            except:
                pass
            
            s.click()
            page.wait_for_timeout(3000)
            page.screenshot(path='stuck_debug_1.png')
            break
            
    browser.close()
