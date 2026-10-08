from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    responses = []
    def on_response(response):
        try:
            if 'api' in response.url or 'quiz' in response.url or 'track' in response.url or 'json' in response.headers.get('content-type', ''):
                data = response.json()
                responses.append({'url': response.url, 'data': data})
        except Exception:
            pass

    page.on('response', on_response)

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(1)

    # Click Semester 1
    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Click Milestone 3
    cards = page.query_selector_all('div:has-text("Milestone 3")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Task 1
    task_btns = page.query_selector_all('button:has-text("Start Learning")')
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Quiz button
    quiz_btn = page.query_selector('button:has-text("quiz"), button:has-text("Quiz")')
    if quiz_btn:
        quiz_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    with open('generated/api_responses.json', 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=2, default=str)

    print(f"Captured {len(responses)} API responses!")
    for r in responses:
        print("  URL:", r['url'])

    browser.close()
