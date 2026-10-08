from playwright.sync_api import sync_playwright
import time

ACT2_TEXT = (
    "My ideal customers are college students and young working professionals aged "
    "18–26 residing in urban Punjab cities like Jalandhar, Ludhiana, and Chandigarh. "
    "They have moderate pocket allowance or entry-level salaries, seeking trendy, "
    "sustainable cotton tote bags and durable gym bottles for college lectures, "
    "daily commuting, and workout sessions."
)

with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=100)
    except Exception:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(1)

    # Click Semester 1
    sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
    if sem_btn:
        sem_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Open Milestone 2
    cards = page.query_selector_all('div:has-text("Milestone 2")')
    for c in cards:
        btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
        if btn:
            btn.click()
            break
    time.sleep(2)
    page.wait_for_load_state('networkidle')

    # Open Task 3 in Milestone 2
    task3_btn = page.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
    if task3_btn:
        task3_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Find the uncompleted activity button: "Start Learning"
    start_btn = page.query_selector('button:has-text("Start Learning")')
    if start_btn:
        start_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        ta = page.query_selector('textarea')
        if ta:
            ta.fill(ACT2_TEXT)
            print("Filled text")
            time.sleep(1)

        sub_btn = page.query_selector('button:has-text("Submit Activity")')
        if sub_btn:
            sub_btn.click()
            time.sleep(3)
            print("Submitted Activity 2!")

    page.screenshot(path='generated/m2_task3_all_done.png', full_page=True)
    browser.close()
