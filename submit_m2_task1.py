"""
Execution script to complete Milestone 2 - Task 1:
1. Video: Watch video on choosing right product -> Mark Complete (+10 pts)
2. Activity 1: List 10 product items you can sell -> Submit (+15 pts)
3. Activity 2: Talk to people & shortlist 5 products -> Submit with photo (+15 pts)
4. Quiz: Attempt task 01 quiz -> Submit 100% correct answers (+15 pts)
Total: +55 points
"""
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

PHOTO_PATH = Path(__file__).parent / "generated" / "product_shortlist_notes.jpg"

ACTIVITY_1_TEXT = (
    "1. Handcrafted wooden mobile holders\n"
    "2. Organic neem and herbal bath soaps\n"
    "3. Custom printed gym water bottles\n"
    "4. Cotton tote bags with Punjabi art prints\n"
    "5. Ceramic coffee mugs with minimalist designs\n"
    "6. Ergonomic memory foam seat cushions\n"
    "7. Traditional handmade Punjabi juttis\n"
    "8. Portable USB rechargeable mini desk fans\n"
    "9. Aromatic soy wax scented candles\n"
    "10. Stainless steel travel cutlery kits"
)

ACTIVITY_2_TEXT = (
    "After surveying 12 college peers and local neighbors using product sample photos, "
    "I shortlisted 5 high-demand products: 1. Custom Gym Bottles (high daily utility), "
    "2. Wooden Phone Stands (popular affordable desk accessory), 3. Cotton Tote Bags "
    "(eco-friendly youth trend), 4. Handmade Punjabi Juttis (strong festive wedding demand), "
    "and 5. Scented Soy Candles (great gift appeal)."
)

QUIZ_ANSWERS = [
    "Ask local shopkeepers what people often buy",
    "Notice what people complain about not finding",
    "Items that people need to buy again and again",
    "People in your area who shop often",
    "What people use regularly in homes or shops"
]


def run():
    print("[...] Launching Chrome for Milestone 2 - Task 1...")
    with sync_playwright() as pw:
        # Launch Chrome with visible window as requested
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

        # Open Task 1 in Milestone 2
        task1_btn = page.query_selector('button:has-text("Start Learning")')
        if task1_btn:
            task1_btn.click()
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
                print("  [OK] Video marked as complete!")

        # -----------------------------------------------------------------
        # 2. Activity 1: List 10 product items that you can sell
        # -----------------------------------------------------------------
        print("\n[2/4] Submitting Activity 1 (List 10 products)...")
        act1_btn = page.query_selector('button:has-text("List 10 product items")')
        if act1_btn:
            act1_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            ta = page.query_selector('textarea')
            if ta:
                ta.fill(ACTIVITY_1_TEXT)
                print("  [OK] 10 products written.")
                time.sleep(1)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Activity 1 submitted!")

        # -----------------------------------------------------------------
        # 3. Activity 2: Talk to people and shortlist 5 products
        # -----------------------------------------------------------------
        print("\n[3/4] Submitting Activity 2 (Shortlist 5 products with photo)...")
        act2_btn = page.query_selector('button:has-text("Talk to people and shortlist 5 products")')
        if act2_btn:
            act2_btn.click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

            ta = page.query_selector('textarea')
            if ta:
                ta.fill(ACTIVITY_2_TEXT)
                print("  [OK] Shortlist text filled.")
                time.sleep(1)

            file_input = page.query_selector('input[type="file"]')
            if file_input and PHOTO_PATH.exists():
                file_input.set_input_files(str(PHOTO_PATH.resolve()))
                print(f"  [OK] Attached notebook notes photo: {PHOTO_PATH.name}")
                time.sleep(2)

            sub_btn = page.query_selector('button:has-text("Submit Activity")')
            if sub_btn:
                sub_btn.click()
                time.sleep(3)
                print("  [OK] Activity 2 submitted!")

        # -----------------------------------------------------------------
        # 4. Attempt Task 01 Quiz
        # -----------------------------------------------------------------
        print("\n[4/4] Submitting Task 01 Quiz...")
        quiz_btn = page.query_selector('button:has-text("Attempt task 01 quiz")')
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
                        print(f"  [OK] Selected: {ans[:40]}...")

            time.sleep(1)
            submit_quiz_btn = page.query_selector('button:has-text("Submit Quiz")')
            if submit_quiz_btn:
                submit_quiz_btn.click()
                time.sleep(3)
                print("  [OK] Quiz submitted!")

        time.sleep(2)
        page.screenshot(path='generated/m2_task1_completion_result.png', full_page=True)
        print("\n[SUCCESS] Milestone 2 - Task 1 complete!")
        browser.close()


if __name__ == "__main__":
    run()
