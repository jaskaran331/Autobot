import json
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()
    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(2)
    
    # Expand Semester 2
    sem_btns = page.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btns.count() >= 2:
        sem_btns.nth(1).click()
        time.sleep(2)
        
    for _ in range(5):
        page.mouse.wheel(0, 1500)
        time.sleep(0.2)
        
    m11 = page.locator('text=Milestone 11').first
    parent = m11.locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "rounded") or contains(@class, "border")][1]')
    parent.locator('button').first.click()
    time.sleep(2)
    
    # Click Task 2
    t2 = page.locator('text=Task 2').first
    if t2.count():
        parent_t2 = t2.locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "rounded") or contains(@class, "border")][1]')
        btn = parent_t2.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")').first
        if btn.count():
            btn.click()
            time.sleep(2)
            
    # Click "Attempt task 02 quiz"
    q_btn = page.locator('text=Attempt task 02 quiz').first
    if q_btn.count():
        q_btn.click()
        time.sleep(2)
        
    # Check Submit Quiz button
    sub_btn = page.locator('button:has-text("Submit Quiz")').first
    print("Submit Quiz count:", sub_btn.count(), "visible:", sub_btn.is_visible() if sub_btn.count() else False)
    
    answers = [
        "To use a strategy that already showed strong results",
        "Engagement and conversion results from the earlier campaign",
        "Keeping the key message and targeting that produced strong results",
        "By adjusting elements such as audience or budget based on earlier insights",
        "Applying similar targeting and messaging strategies",
        "Reviewing campaign metrics to understand the reasons for success"
    ]
    
    for ans in answers:
        loc = page.locator(f'text="{ans}"').first
        if loc.count():
            try:
                loc.scroll_into_view_if_needed()
                loc.click(force=True)
                print(f"Clicked '{ans[:35]}...'")
                time.sleep(0.4)
            except Exception as e:
                print(f"Error clicking: {e}")
                
    time.sleep(1)
    if sub_btn.is_enabled():
        print("Submit button is ENABLED! Clicking Submit Quiz...")
        sub_btn.scroll_into_view_if_needed()
        sub_btn.click(force=True)
        time.sleep(3)
        page.screenshot(path='artifacts/m11_t2_quiz_submitted.png', full_page=True)
        print("Quiz submitted! Screenshot saved.")
    else:
        print("Submit button is NOT enabled!")
        page.screenshot(path='artifacts/m11_t2_quiz_fail.png', full_page=True)
        
    browser.close()
