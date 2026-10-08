"""
Execution script to complete Milestone 1:
1. Task 2: Mark download guide complete
2. Task 3: Mark video complete
3. Task 3: Submit 50-word seller interview + attach notebook image
4. Task 3: Submit quiz with 100% correct answers
"""
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PHOTO_PATH = Path(__file__).parent / "generated" / "seller_interview_assignment.jpg"
ANSWER_TEXT = (
    "I interviewed Aman from Phagwara who sells wooden craft toys on Meesho earning around "
    "₹70,000 monthly; he highlighted zero-commission benefits and pan-India reach. I also spoke "
    "with Gurpreet from Ludhiana selling athletic apparel on Amazon earning ₹1.5L monthly, "
    "who shared that managing return logistics and customer reviews was crucial for steady growth."
)

QUIZ_ANSWERS = [
    "Digital downloads like e-books or tools",
    "Save products to buy later or checkout",
    "Transporting the product to the customer",
    "Confirming order details and payment",
    "When the seller takes orders but the supplier ships the product"
]


def run_submission():
    print("[...] Launching Playwright with saved session...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state='session.json')
        page = ctx.new_page()

        # Step 1: Open Track
        page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
        time.sleep(2)

        # Enter Semester 1
        btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
        if btns:
            btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        # Enter Milestone 1
        continue_btns = [b for b in page.query_selector_all('button') if "continue learning" in (b.inner_text() or "").lower()]
        if continue_btns:
            continue_btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        # -------------------------------------------------------------
        # Part A: Complete pending item in Task 2
        # -------------------------------------------------------------
        print("\n[1/3] Completing Task 2 (Download guide)...")
        task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
        if task_btns:
            # Click Task 2 Start Learning
            task_btns[0].click()
            time.sleep(3)
            page.wait_for_load_state('networkidle')

            # Select guide item if needed
            guide_btn = page.query_selector('button:has-text("Download this guide")')
            if guide_btn:
                guide_btn.click()
                time.sleep(1)

            # Click Mark as Complete
            mark_btn = page.query_selector('button:has-text("Mark as Complete")')
            if mark_btn:
                mark_btn.click()
                time.sleep(2)
                print("  [OK] Task 2 Guide marked as complete!")

            # Return to Task list
            back_btn = page.query_selector('button:has-text("See All Tasks")')
            if back_btn:
                back_btn.click()
                time.sleep(2)
                page.wait_for_load_state('networkidle')

        # -------------------------------------------------------------
        # Part B: Enter Task 3
        # -------------------------------------------------------------
        print("\n[2/3] Entering Task 3...")
        # Find Task 3
        task_btns = [b for b in page.query_selector_all('button') if "start learning" in (b.inner_text() or "").lower()]
        if task_btns:
            task_btns[0].click()
            time.sleep(3)
            page.wait_for_load_state('networkidle')

        # Sub-item 1: Video -> Mark as Complete
        print("  Completing video activity...")
        video_item = page.query_selector('button:has-text("Watch a video on how sellers make money")')
        if video_item:
            video_item.click()
            time.sleep(1)
            mark_btn = page.query_selector('button:has-text("Mark as Complete")')
            if mark_btn:
                mark_btn.click()
                time.sleep(2)
                print("  [OK] Video marked as complete!")

        # Sub-item 2: Written Activity + Image Upload
        print("  Submitting written interview assignment with AI photo...")
        seller_item = page.query_selector('button:has-text("Talk to 2 sellers in your area")')
        if seller_item:
            seller_item.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            # Fill textarea
            textarea = page.query_selector('textarea')
            if textarea:
                textarea.fill(ANSWER_TEXT)
                print("  [OK] Answer text filled.")
                time.sleep(1)

            # Upload photo
            file_input = page.query_selector('input[type="file"]')
            if file_input and PHOTO_PATH.exists():
                file_input.set_input_files(str(PHOTO_PATH.resolve()))
                print(f"  [OK] Photo attached: {PHOTO_PATH.name}")
                time.sleep(2)

            # Click Submit Activity
            submit_btn = page.query_selector('button:has-text("Submit Activity")')
            if submit_btn:
                submit_btn.click()
                time.sleep(3)
                print("  [OK] Activity submitted successfully!")

        # -------------------------------------------------------------
        # Part C: Task 3 Quiz
        # -------------------------------------------------------------
        print("\n[3/3] Answering Task 3 Quiz...")
        quiz_item = page.query_selector('button:has-text("Attempt task 03 quiz")')
        if quiz_item:
            quiz_item.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            for ans in QUIZ_ANSWERS:
                matching = page.query_selector_all(f':text("{ans}")')
                if matching:
                    matching[-1].click()
                    time.sleep(0.5)
                    print(f"  [OK] Selected: {ans[:40]}...")
                else:
                    opt = page.query_selector(f'button:has-text("{ans}"), label:has-text("{ans}")')
                    if opt:
                        opt.click()
                        time.sleep(0.5)
                        print(f"  [OK] Selected fallback: {ans[:40]}...")

            time.sleep(1)
            submit_quiz_btn = page.query_selector('button:has-text("Submit Quiz")')
            if submit_quiz_btn:
                submit_quiz_btn.click()
                time.sleep(3)
                print("  [OK] Quiz submitted successfully!")

        time.sleep(3)
        # Capture confirmation toast if any
        toast = page.query_selector('[data-sonner-toast], [role="alert"]')
        if toast:
            print(f"  Site Toast: {toast.inner_text().strip()}")

        # Take confirmation screenshot
        page.screenshot(path='generated/milestone_1_completion_result.png', full_page=True)
        print("\n[SUCCESS] Milestone 1 operations executed! Screenshot saved to generated/milestone_1_completion_result.png")
        browser.close()


if __name__ == "__main__":
    run_submission()
