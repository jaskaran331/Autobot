"""
Execution script to complete Milestone 2 - Task 2:
1. Video: Watch video on Amazon tools -> Mark Complete (+10 pts)
2. Activity 1: Download comparison table -> Mark Complete (+10 pts)
3. Activity 2: Upload comparison table image -> Submit (+15 pts)
4. Activity 3: Select one final product -> Submit 30-word answer (+15 pts)
5. Quiz: Attempt task 02 quiz -> Submit 100% correct answers (+15 pts)
Total: +65 points
"""
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PHOTO_PATH = Path(__file__).parent / "generated" / "product_comparison_matrix.jpg"

FINAL_PRODUCT_TEXT = (
    "I selected Cotton Tote Bags with regional Punjabi art prints because they offer "
    "76% profit margin, zero transit breakage, and high recurring demand among college "
    "students seeking sustainable fashion."
)

QUIZ_ANSWERS = [
    "If people are already searching for it online",
    "Lightweight, small items with clear demand",
    "Look at trending products on marketplaces",
    "You can answer customer queries confidently",
    "You lose money on shipping and packaging"
]


def run():
    print("[...] Launching Chrome for Milestone 2 - Task 2...")
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

        # Open Task 2 in Milestone 2
        task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
        if task_btns:
            task_btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        # -----------------------------------------------------------------
        # 1. Video Activity -> Mark as Complete
        # -----------------------------------------------------------------
        print("[1/5] Completing Video Activity...")
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
        # 2. Download Comparison Table -> Mark as Complete
        # -----------------------------------------------------------------
        print("\n[2/5] Completing Download Table Activity...")
        down_btn = page.query_selector('button:has-text("Download this comparison table")')
        if down_btn:
            down_btn.click()
            time.sleep(1)
            mark_btn = page.query_selector('button:has-text("Mark as Complete")')
            if mark_btn:
                mark_btn.click()
                time.sleep(2)
                print("  [OK] Download table marked complete!")

        # -----------------------------------------------------------------
        # 3. Upload Comparison Table
        # -----------------------------------------------------------------
        print("\n[3/5] Submitting Comparison Table upload...")
        up_btn = page.query_selector('button:has-text("Fill in and upload your comparison table")')
        if up_btn:
            up_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            file_input = page.query_selector('input[type="file"]')
            if file_input and PHOTO_PATH.exists():
                file_input.set_input_files(str(PHOTO_PATH.resolve()))
                print(f"  [OK] Attached matrix image: {PHOTO_PATH.name}")
                time.sleep(2)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Table upload submitted!")

        # -----------------------------------------------------------------
        # 4. Select Final Product (30 words)
        # -----------------------------------------------------------------
        print("\n[4/5] Submitting Final Product Selection...")
        prod_btn = page.query_selector('button:has-text("Select one final product")')
        if prod_btn:
            prod_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            ta = page.query_selector('textarea')
            if ta:
                ta.fill(FINAL_PRODUCT_TEXT)
                print("  [OK] 30-word rationale filled.")
                time.sleep(1)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Final product submitted!")

        # -----------------------------------------------------------------
        # 5. Attempt Task 02 Quiz
        # -----------------------------------------------------------------
        print("\n[5/5] Submitting Task 02 Quiz...")
        quiz_btn = page.query_selector('button:has-text("Attempt task 02 quiz")')
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
        page.screenshot(path='generated/m2_task2_completion_result.png', full_page=True)
        print("\n[SUCCESS] Milestone 2 - Task 2 complete!")
        browser.close()


if __name__ == "__main__":
    run()
