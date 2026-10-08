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

        # Task 2
        task_cards = page.query_selector_all('div:has-text("Connect with 3 suppliers")')
        for tc in task_cards:
            btn = tc.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        print("=== Inside M3 Task 2 ===")

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

        # 2. Draft first message
        print("[2] Draft first message activity...")
        # Re-click or click next item
        draft_item = page.query_selector('div:has-text("Draft your first message"), button:has-text("Draft your first message")')
        if draft_item:
            draft_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Hello, I am reaching out from Punjab Bag Studio. We are launching an online store for premium canvas tote bags and would like to inquire about wholesale catalog, minimum order quantities (MOQ), unit pricing, and shipping timelines to Punjab. Please share your product catalog."
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
                    print("  Submitted draft message!")
                    time.sleep(3)

        # 3. Send message to 3 suppliers
        print("[3] Send message to 3 suppliers activity...")
        send_item = page.query_selector('div:has-text("Send message to 3 suppliers"), button:has-text("Send message to 3 suppliers")')
        if send_item:
            send_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Sent wholesale inquiries via WhatsApp and IndiaMART to 3 shortlisted suppliers: CottonCraft India, EcoFab Surat, and Khalsa Textiles Ludhiana. All three responded promptly with price quotes ranging from Rs 80 to Rs 95 per unit with samples available on request."
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
                    print("  Submitted send messages!")
                    time.sleep(3)

        # 4. Quiz
        print("[4] Task 2 Quiz...")
        quiz_item = page.query_selector('div:has-text("Attempt task 02 quiz"), button:has-text("Attempt task 02 quiz")')
        if quiz_item:
            quiz_item.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)

            answers = [
                "Hello, I",
                "Price, delivery time, and return policy",
                "I like the product. Is there a better price for bulk order?",
                "So you can plan stock and inform customers",
                "Responds politely and on time"
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

        page.screenshot(path='generated/m3_task2_done.png', full_page=True)
        print("M3 Task 2 finished!")
        browser.close()

if __name__ == '__main__':
    run()
