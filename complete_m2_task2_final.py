from playwright.sync_api import sync_playwright
import time

FINAL_PRODUCT_TEXT = (
    "I selected Cotton Tote Bags with regional Punjabi art prints because they offer "
    "76% profit margin, zero transit breakage, and high recurring demand among college "
    "students seeking sustainable fashion."
)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
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

    # Open Task 2 in Milestone 2
    task2_btn = page.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
    if task2_btn:
        task2_btn.click()
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
            ta.fill(FINAL_PRODUCT_TEXT)
            print("Filled text")
            time.sleep(1)

        sub_btn = page.query_selector('button:has-text("Submit Activity")')
        if sub_btn:
            sub_btn.click()
            time.sleep(3)
            print("Submitted final product!")

    page.screenshot(path='generated/m2_task2_all_done.png', full_page=True)
    browser.close()
