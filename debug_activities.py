from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    c = b.new_context(storage_state='session.json')
    pg = c.new_page()
    pg.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    pg.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")').click()
    time.sleep(3)
    
    cards = pg.query_selector_all('div:has-text("Milestone 3")')
    for card in cards:
        btn = card.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if btn and btn.is_visible():
            btn.click()
            time.sleep(3)
            break
            
    # Print tasks
    print("Tasks on page:")
    tcards = pg.query_selector_all('.chakra-stack')
    for tc in tcards:
        if "Task" in tc.inner_text():
            print("---", tc.inner_text().split("\n")[0])
            
    # Try to click task 1
    tcards = pg.query_selector_all('div:has-text("Search for Indian suppliers")')
    for tc in tcards:
        btn = tc.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if btn and btn.is_visible():
            btn.click()
            time.sleep(3)
            break
            
    print("\nActivities in pane:")
    acts = pg.query_selector_all('.chakra-text, p, h2, h3, h4, span')
    for a in acts:
        text = a.inner_text().strip()
        if len(text) > 10 and "\n" not in text:
            print(text)
