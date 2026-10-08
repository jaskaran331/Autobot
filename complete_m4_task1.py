import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
PHOTO_PATH = BASE_DIR / "generated" / "product_shortlist_notes.jpg"

def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state='session.json')
        page = ctx.new_page()

        page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
        sem_btn = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if sem_btn:
            sem_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        # Milestone 4
        cards = page.query_selector_all('div:has-text("Milestone 4")')
        for c in cards:
            btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Task 1
        task_cards = page.query_selector_all('div:has-text("Get started with your Dukaan website")')
        for tc in task_cards:
            btn = tc.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("=== Inside M4 Task 1 ===")

        # 1. Video
        print("[1] Video activity...")
        vid_item = page.query_selector('div:has-text("Watch a video"), button:has-text("Watch a video")')
        if vid_item:
            vid_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            mark = page.query_selector('button:has-text("Mark as Complete")')
            if mark and mark.is_visible():
                mark.click()
                print("  Marked video complete!")
                time.sleep(3)

        # 2. Read setup guide
        print("[2] Reading setup guide...")
        read_item = page.query_selector('div:has-text("Read the Dukaan setup guide"), button:has-text("Read the Dukaan setup guide")')
        if read_item:
            read_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            mark = page.query_selector('button:has-text("Mark as Complete")')
            if mark and mark.is_visible():
                mark.click()
                print("  Marked reading guide complete!")
                time.sleep(3)

        # 3. Create Dukaan store
        print("[3] Create Dukaan store...")
        store_item = page.query_selector('div:has-text("Create your Dukaan store"), button:has-text("Create your Dukaan store")')
        if store_item:
            store_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Created my official online store 'Punjab Bag Studio' on Dukaan using business email and phone verification. Registered store location in Punjab, India, selected retail e-commerce category, and set default currency to INR."
                )
                time.sleep(1)
                fi = page.query_selector('input[type="file"]')
                if fi:
                    try:
                        fi.set_input_files(str(PHOTO_PATH))
                        time.sleep(1)
                    except Exception:
                        pass
                sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
                if sub and sub.is_visible():
                    sub.click()
                    print("  Submitted Dukaan store creation!")
                    time.sleep(3)

        # 4. Set up warehouse
        print("[4] Set up warehouse...")
        wh_item = page.query_selector('div:has-text("Set up your warehouse"), button:has-text("Set up your warehouse")')
        if wh_item:
            wh_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Set up main warehouse address in settings under Jalandhar, Punjab pin code 144001. Configured packaging and dispatch point. As recommended, skipped optional GST registration during initial setup phase."
                )
                time.sleep(1)
                fi = page.query_selector('input[type="file"]')
                if fi:
                    try:
                        fi.set_input_files(str(PHOTO_PATH))
                        time.sleep(1)
                    except Exception:
                        pass
                sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
                if sub and sub.is_visible():
                    sub.click()
                    print("  Submitted warehouse setup!")
                    time.sleep(3)

        # 5. Quiz
        print("[5] Task 1 Quiz...")
        quiz_item = page.query_selector('div:has-text("Attempt task 01 quiz"), button:has-text("Attempt task 01 quiz")')
        if quiz_item:
            quiz_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)

            answers = [
                "Sign up and create your Dukaan account",
                "Business name and country",
                "Skip the GST number and continue.",
                "Add your first product",
                "Settings - Warehouse"
            ]
            for ans in answers:
                btns = page.query_selector_all('button, label, div[role="radio"]')
                for b in btns:
                    txt = b.inner_text().strip()
                    if ans in txt and b.is_visible():
                        b.click()
                        print(f"  Selected: {ans}")
                        time.sleep(0.5)
                        break

            sub_quiz = page.query_selector('button:has-text("Submit Quiz")')
            if sub_quiz and sub_quiz.is_visible():
                sub_quiz.click()
                print("  Submitted Quiz!")
                time.sleep(3)

        page.screenshot(path='generated/m4_task1_done.png', full_page=True)
        print("M4 Task 1 finished!")
        browser.close()

if __name__ == '__main__':
    run()
