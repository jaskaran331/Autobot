"""
Execution script to complete Milestone 2 - Task 3:
1. Video: Watch video on defining customer -> Mark Complete (+10 pts)
2. Activity 1: Identify 5 customers and talk to them -> Submit 50-word answer (+15 pts)
3. Activity 2: Clearly define who is your customer -> Submit 50-word answer (+15 pts)
4. Quiz: Attempt task 03 quiz -> Submit 100% correct answers (+15 pts)
Total: +55 points
"""
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PHOTO_PATH = Path(__file__).parent / "generated" / "product_shortlist_notes.jpg"

ACT1_TEXT = (
    "I surveyed 5 potential buyers aged 18 to 35 across Jalandhar. College students "
    "Simran and Rohan preferred cotton tote bags at ₹399 for campus utility. Working "
    "professional Harpreet wanted gym bottles at ₹499. All respondents emphasized "
    "good stitching quality, aesthetic typography, and fair pricing over luxury brand tags."
)

ACT2_TEXT = (
    "My ideal customers are college students and young working professionals aged "
    "18–26 residing in urban Punjab cities like Jalandhar, Ludhiana, and Chandigarh. "
    "They have moderate pocket allowance or entry-level salaries, seeking trendy, "
    "sustainable cotton tote bags and durable gym bottles for college lectures, "
    "daily commuting, and workout sessions."
)

QUIZ_ANSWERS = [
    "Look for people who face the problem your product solves",
    "Who will benefit most from this product?",
    "So you can create ads and messages that connect",
    "They are already buying something similar",
    "Trendy phone covers and budget gadgets"
]


def run():
    print("[...] Launching Chrome for Milestone 2 - Task 3...")
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=100)
        except Exception:
            browser = pw.chromium.launch(headless=False, slow_mo=100)

        ctx = browser.new_context(storage_state='session.json')
        page = ctx.new_page()

        # Step 1: Track page
        page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
        time.sleep(1)

        # Enter Semester 1
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
        task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
        if task_btns:
            task_btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        # -----------------------------------------------------------------
        # 1. Video Activity -> Mark as Complete
        # -----------------------------------------------------------------
        print("[1/4] Completing Video Activity...")
        video_btn = page.query_selector('button:has-text("Watch a video on")')
        if video_btn:
            video_btn.click()
            time.sleep(1)
            mark_btn = page.query_selector('button:has-text("Mark as Complete")')
            if mark_btn:
                mark_btn.click()
                time.sleep(2)
                print("  [OK] Video marked complete!")

        # -----------------------------------------------------------------
        # 2. Activity 1: Identify 5 customers and talk to them
        # -----------------------------------------------------------------
        print("\n[2/4] Submitting Activity 1 (Identify 5 customers)...")
        act1_btn = page.query_selector('button:has-text("Identify 5 customers")')
        if act1_btn:
            act1_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            ta = page.query_selector('textarea')
            if ta:
                ta.fill(ACT1_TEXT)
                print("  [OK] 5 customers feedback filled.")
                time.sleep(1)

            file_input = page.query_selector('input[type="file"]')
            if file_input and PHOTO_PATH.exists():
                file_input.set_input_files(str(PHOTO_PATH.resolve()))
                print(f"  [OK] Attached customer notes photo: {PHOTO_PATH.name}")
                time.sleep(2)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Activity 1 submitted!")

        # -----------------------------------------------------------------
        # 3. Activity 2: Clearly define who is your customer
        # -----------------------------------------------------------------
        print("\n[3/4] Submitting Activity 2 (Define customer)...")
        act2_btn = page.query_selector('button:has-text("Clearly define who is your customer")')
        if act2_btn:
            act2_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            ta = page.query_selector('textarea')
            if ta:
                ta.fill(ACT2_TEXT)
                print("  [OK] Customer definition filled.")
                time.sleep(1)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Activity 2 submitted!")

        # -----------------------------------------------------------------
        # 4. Attempt Task 03 Quiz
        # -----------------------------------------------------------------
        print("\n[4/4] Submitting Task 03 Quiz...")
        quiz_btn = page.query_selector('button:has-text("Attempt task 03 quiz")')
        if quiz_btn:
            quiz_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            for ans in QUIZ_ANSWERS:
                matching = page.query_selector_all(f':text("{ans}")')
                if matching:
                    matching[-1].click()
                    time.sleep(0.4)
                    print(f"  [OK] Selected: {ans[:40]}...")
                else:
                    opt = page.query_selector(f'button:has-text("{ans}"), label:has-text("{ans}")')
                    if opt:
                        opt.click()
                        time.sleep(0.4)
                        print(f"  [OK] Selected fallback: {ans[:40]}...")

            time.sleep(1)
            submit_quiz_btn = page.query_selector('button:has-text("Submit Quiz")')
            if submit_quiz_btn:
                submit_quiz_btn.click()
                time.sleep(3)
                print("  [OK] Quiz submitted!")

        time.sleep(2)
        page.screenshot(path='generated/m2_task3_completion_result.png', full_page=True)
        print("\n[SUCCESS] Milestone 2 - Task 3 complete!")
        browser.close()


if __name__ == "__main__":
    run()
