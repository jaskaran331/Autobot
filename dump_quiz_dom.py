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
    
    # Task 2
    t2_btn = page.locator('div:has-text("Task 2") button:has-text("Start Learning"), div:has-text("Task 2") button:has-text("Continue Learning")').first
    if t2_btn.count():
        t2_btn.click()
        time.sleep(2)
        
    # Quiz item
    quiz_card = page.locator('div:has-text("Attempt task 02 quiz"), button:has-text("Attempt task 02 quiz")').first
    if quiz_card.count():
        quiz_card.click()
        time.sleep(2)
        
    # Dump HTML of right panel
    content = page.content()
    with open('artifacts/full_quiz_page.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved artifacts/full_quiz_page.html")
    browser.close()
