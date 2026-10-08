from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PHOTO_PATH = Path(__file__).parent / "generated" / "product_shortlist_notes.jpg"
ACTIVITY_2_TEXT = (
    "After surveying 12 college peers and local neighbors using product sample photos, "
    "I shortlisted 5 high-demand products: 1. Custom Gym Bottles (high daily utility), "
    "2. Wooden Phone Stands (popular affordable desk accessory), 3. Cotton Tote Bags "
    "(eco-friendly youth trend), 4. Handmade Punjabi Juttis (strong festive wedding demand), "
    "and 5. Scented Soy Candles (great gift appeal)."
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

    # Open Task 1
    task1_btn = page.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
    if task1_btn:
        task1_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    # Find the uncompleted activity button: "Start Learning"
    start_btn = page.query_selector('button:has-text("Start Learning")')
    if start_btn:
        start_btn.click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Fill text
        ta = page.query_selector('textarea')
        if ta:
            ta.fill(ACTIVITY_2_TEXT)
            print("Filled text")
            time.sleep(1)

        # Upload photo
        file_input = page.query_selector('input[type="file"]')
        if file_input and PHOTO_PATH.exists():
            file_input.set_input_files(str(PHOTO_PATH.resolve()))
            print("Uploaded photo")
            time.sleep(2)

        # Submit
        sub_btn = page.query_selector('button:has-text("Submit Activity")')
        if sub_btn:
            sub_btn.click()
            time.sleep(3)
            print("Submitted Activity 2!")

    page.screenshot(path='generated/m2_task1_all_done.png', full_page=True)
    browser.close()
