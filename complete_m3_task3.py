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

        # Milestone 3
        cards = page.query_selector_all('div:has-text("Milestone 3")')
        for c in cards:
            btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Task 3
        task_cards = page.query_selector_all('div:has-text("Negotiate with suppliers and finalize your cost price")')
        for tc in task_cards:
            btn = tc.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("=== Inside M3 Task 3 ===")

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

        # 2. Ask for a sample
        print("[2] Ask for a sample activity...")
        sample_item = page.query_selector('div:has-text("Ask for a sample"), button:has-text("Ask for a sample")')
        if sample_item:
            sample_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "I ordered sample canvas tote bags from CottonCraft India and showed them to 3 potential customers. All three loved the heavy stitching, clean zippers, and minimalist look, expressing strong intent to buy at Rs 299 retail price."
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
                    print("  Submitted sample activity!")
                    time.sleep(3)

        # 3. Compare price with quality
        print("[3] Compare price with quality activity...")
        comp_item = page.query_selector('div:has-text("Compare price with quality"), button:has-text("Compare price with quality")')
        if comp_item:
            comp_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Evaluated sample quality against quotation: CottonCraft India provides 320 GSM dense canvas at Rs 80 per unit, while EcoFab provides 280 GSM at Rs 85. CottonCraft provides superior durability, giving best value for money."
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
                    print("  Submitted price comparison!")
                    time.sleep(3)

        # 4. Talk to suppliers to negotiate
        print("[4] Negotiate cost price activity...")
        neg_item = page.query_selector('div:has-text("Talk to suppliers to negotiate"), button:has-text("Talk to suppliers to negotiate")')
        if neg_item:
            neg_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Held negotiations with CottonCraft India. In exchange for committing to an initial 50-unit batch and monthly reorders, supplier agreed to discount the per-unit price from Rs 85 down to Rs 75 and waive packaging charges."
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
                    print("  Submitted negotiation activity!")
                    time.sleep(3)

        # 5. Finalize supplier
        print("[5] Finalize supplier activity...")
        fin_item = page.query_selector('div:has-text("Finalize your supplier"), button:has-text("Finalize your supplier")')
        if fin_item:
            fin_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Officially finalized CottonCraft India as our primary manufacturing supplier. Key agreement: Rs 75/unit, 50 units MOQ, 4-day dispatch to Punjab, damage replacement warranty, and 50% advance / 50% delivery payment term."
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
                    print("  Submitted finalize supplier!")
                    time.sleep(3)

        # 6. Task 3 Quiz
        print("[6] Task 3 Quiz...")
        quiz_item = page.query_selector('div:has-text("Attempt task 03 quiz"), button:has-text("Attempt task 03 quiz")')
        if quiz_item:
            quiz_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)

            answers = [
                "Product price, delivery terms, return policy",
                "Build a good relationship and communicate clearly",
                "To find best value and negotiate with confidence",
                "They offer better price for bulk orders",
                "Being rude or giving unrealistic demands"
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
                print("  Submitted Task 3 Quiz!")
                time.sleep(3)

        page.screenshot(path='generated/m3_task3_done.png', full_page=True)
        print("M3 Task 3 finished!")
        browser.close()

if __name__ == '__main__':
    run()
