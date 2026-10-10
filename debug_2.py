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
        try:
            parent = page.evaluate("(el) => { let p = el.closest('.bg-white'); return p ? p.innerText : ''; }", s)
            if 'Semester 1' in parent: continue
            if s.is_visible():
                s.click()
                break
        except: pass
    page.wait_for_timeout(3000)
    
    conts = page.query_selector_all('button >> text="Continue Learning"')
    for c in conts:
        if c.is_visible():
            c.click()
            break
    page.wait_for_timeout(3000)
    
    tasks = page.query_selector_all('button >> text="Start Learning"')
    for t in tasks:
        if t.is_visible():
            t.click()
            break
            
    page.wait_for_timeout(4000)
    
    page.screenshot(path='stuck_activity_real.png')
    html = page.evaluate("document.body.innerHTML")
    with open('stuck_activity.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    browser.close()
