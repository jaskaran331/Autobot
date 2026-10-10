import time
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
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
    
    # Click "See All Tasks" if needed, or click Task 2
    t2 = page.locator('text=Task 2').first
    if t2.count():
        print("Found Task 2 text, clicking parent...")
        parent_t2 = t2.locator('xpath=ancestor::div[contains(@class, "card") or contains(@class, "rounded") or contains(@class, "border")][1]')
        btn = parent_t2.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")').first
        if btn.count():
            btn.click()
            time.sleep(2)
            
    # Click "Attempt task 02 quiz"
    q_btn = page.locator('text=Attempt task 02 quiz').first
    if q_btn.count():
        print("Found Attempt task 02 quiz, clicking...")
        q_btn.click()
        time.sleep(2)
        
    page.screenshot(path='artifacts/test_quiz_open.png', full_page=True)
    
    # Check Submit Quiz button
    sub_btn = page.locator('button:has-text("Submit Quiz")').first
    print("Submit Quiz count:", sub_btn.count(), "visible:", sub_btn.is_visible() if sub_btn.count() else False, "enabled:", sub_btn.is_enabled() if sub_btn.count() else False)
    
    # Answers for Task 2 quiz:
    answers = [
        "To use a strategy that already showed strong results",
        "Engagement and conversion results from the earlier campaign",
        "Keeping the key message and targeting that produced strong results",
        "By adjusting elements such as audience or budget based on earlier insights",
        "Applying similar targeting and messaging strategies",
        "Reviewing campaign metrics to understand the reasons for success"
    ]
    
    for ans in answers:
        # Try to locate by text
        loc = page.locator(f'text="{ans}"').first
        if loc.count():
            print(f"Found option for '{ans[:30]}...', visible: {loc.is_visible()}")
            try:
                loc.scroll_into_view_if_needed()
                loc.click(force=True)
                print(f"  [OK] Clicked '{ans[:30]}...'")
                time.sleep(0.5)
            except Exception as e:
                print(f"  [WARN] Failed to click: {e}")
        else:
            print(f"Option not found for '{ans[:30]}...'")
            
    time.sleep(1)
    print("Submit Quiz enabled now?:", sub_btn.is_enabled())
    page.screenshot(path='artifacts/test_quiz_answered.png', full_page=True)
    
    browser.close()
