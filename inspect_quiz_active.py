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
        
    # Save screenshot and HTML fragment of quiz
    page.screenshot(path='artifacts/active_quiz.png', full_page=True)
    
    # Look for question elements and options
    html = page.evaluate("""() => {
        const quizContainer = document.querySelector('div:has(button:has-text("Submit Quiz"))') || document.body;
        return document.body.innerHTML;
    }""")
    
    with open('artifacts/quiz_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    # Find all inputs, buttons, options in quiz
    opts = page.evaluate("""() => {
        const results = [];
        const items = document.querySelectorAll('button, label, input, [role="radio"], [role="checkbox"]');
        for (const item of items) {
            results.push({
                tag: item.tagName,
                type: item.getAttribute('type'),
                role: item.getAttribute('role'),
                text: item.innerText ? item.innerText.trim().slice(0, 60) : '',
                className: item.className
            });
        }
        return results;
    }""")
    print("Found elements:", len(opts))
    for o in opts[:30]:
        print(o)
        
    browser.close()
