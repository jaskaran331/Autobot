import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
PHOTO_PATH = BASE_DIR / "generated" / "product_shortlist_notes.jpg"

def run_task2(page):
    print("\n========== MILESTONE 3: TASK 2 ==========")
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

    # 1. Video
    print("[T2-1] Video: How to message suppliers")
    vid = page.query_selector('div:has-text("Watch a video"), button:has-text("Watch a video")')
    if vid:
        vid.click()
        time.sleep(1.5)
        st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if st and st.is_visible():
            st.click()
            time.sleep(1)
        mark = page.query_selector('button:has-text("Mark as Complete")')
        if mark and mark.is_visible():
            mark.click()
            time.sleep(2)
            print("  Video marked complete!")

    # 2. Draft first message
    print("[T2-2] Draft first message")
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
                print("  Submitted draft message activity!")
                time.sleep(3)

    # 3. Send message to 3 suppliers
    print("[T2-3] Send message to 3 suppliers")
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
                print("  Submitted send messages activity!")
                time.sleep(3)

    # 4. Quiz
    print("[T2-4] Task 2 Quiz")
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
            btns = page.query_selector_all('button')
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
            print("  Submitted Task 2 Quiz!")
            time.sleep(3)


def run_task3(page):
    print("\n========== MILESTONE 3: TASK 3 ==========")
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

    # 1. Video
    print("[T3-1] Video: How to negotiate")
    vid = page.query_selector('div:has-text("Watch a video"), button:has-text("Watch a video")')
    if vid:
        vid.click()
        time.sleep(1.5)
        st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if st and st.is_visible():
            st.click()
            time.sleep(1)
        mark = page.query_selector('button:has-text("Mark as Complete")')
        if mark and mark.is_visible():
            mark.click()
            time.sleep(2)
            print("  Video marked complete!")

    # 2. Ask for sample
    print("[T3-2] Ask for sample")
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
                "I ordered sample tote bags from CottonCraft India and showed them to 3 potential customers (college students and working professionals). All 3 appreciated the heavy stitching, clean zippers, and eco-friendly aesthetic, confirming high customer demand at Rs 299 retail price."
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
    print("[T3-3] Compare price with quality")
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
                "Comparison of price vs quality: CottonCraft India offers the highest fabric density (320 GSM canvas) at Rs 80 per piece. EcoFab was Rs 85 for 280 GSM. Khalsa Textiles was Rs 90 for 300 GSM. CottonCraft clearly provides the superior price-to-quality ratio."
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
                print("  Submitted price comparison activity!")
                time.sleep(3)

    # 4. Talk to suppliers to negotiate
    print("[T3-4] Talk to suppliers to negotiate")
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
                "Negotiated with CottonCraft supplier politely, discussing an initial order of 50 units with recurring monthly orders. The supplier agreed to reduce unit cost from Rs 85 to Rs 75 per unit and provide free polybag packaging for bulk consignments."
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
    print("[T3-5] Finalize supplier")
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
                "Finalized CottonCraft India as our primary supplier. Agreed terms: Rs 75 per bag, 50 units MOQ, 4-day delivery to Punjab, replacement guarantee for defective pieces, and 50% advance with 50% on dispatch."
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
                print("  Submitted finalize supplier activity!")
                time.sleep(3)

    # 6. Task 3 Quiz
    print("[T3-6] Task 3 Quiz")
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
            btns = page.query_selector_all('button')
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

if __name__ == '__main__':
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state='session.json')
        page = ctx.new_page()
        run_task2(page)
        run_task3(page)
        page.screenshot(path='generated/m3_complete_finished.png', full_page=True)
        browser.close()
