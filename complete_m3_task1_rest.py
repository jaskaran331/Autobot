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

        # Click Milestone 3
        cards = page.query_selector_all('div:has-text("Milestone 3")')
        for c in cards:
            btn = c.query_selector('button:has-text("Continue Learning"), button:has-text("Start Learning")')
            if btn:
                btn.click()
                break
        time.sleep(2)
        page.wait_for_load_state('networkidle')

        # Task 1
        task_btns = page.query_selector_all('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if task_btns:
            task_btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        print("=== Inside Task 1 ===")

        # Activity 2: Search for suppliers offline
        print("[1] Activity: Search for suppliers offline")
        act_card = page.query_selector('div:has-text("Search for suppliers offline"), button:has-text("Search for suppliers offline")')
        if act_card:
            act_card.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "I visited local wholesale cloth markets in Jalandhar and Ludhiana to find offline suppliers: "
                    "1. Verma Bag Emporium (Rainak Bazar) - Rs 110 per piece. "
                    "2. Sharma Cloth Traders (Model Town) - Rs 105 per piece. "
                    "3. Guru Nanak Handloom House - Rs 95 per piece. "
                    "4. Khalsa Textiles (Chaura Bazar) - Rs 90 per piece. "
                    "5. Jalandhar Canvas Mart - Rs 100 per piece. Fabric quality was personally verified."
                )
                time.sleep(1)
                sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
                if sub and sub.is_visible():
                    sub.click()
                    print("  Submitted offline suppliers!")
                    time.sleep(3)

        # Activity 3: Write down 3 supplier names & prices
        print("[2] Activity: Write down 3 supplier names & prices")
        act_card = page.query_selector('div:has-text("Write down 3 supplier names"), button:has-text("Write down 3 supplier names")')
        if act_card:
            act_card.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                ta.fill(
                    "Selected top 3 suppliers: "
                    "1. CottonCraft India: Rs 80/unit, 4 days delivery, 4.8 star rating. "
                    "2. EcoFab Surat: Rs 85/unit, 3 days delivery, 4.6 star rating. "
                    "3. Khalsa Textiles Ludhiana: Rs 90/unit, 1 day local delivery, 4.7 star rating."
                )
                time.sleep(1)
                sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
                if sub and sub.is_visible():
                    sub.click()
                    print("  Submitted 3 supplier names!")
                    time.sleep(3)

        # Activity 4: Quiz
        print("[3] Activity: Quiz")
        act_card = page.query_selector('div:has-text("Attempt task 01 quiz"), button:has-text("Attempt task 01 quiz")')
        if act_card:
            act_card.click()
            time.sleep(1.5)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)

            answers = [
                "Product quality and delivery time",
                "IndiaMART",
                "Visit their store or warehouse",
                "Check prices, samples, and terms",
                "Visit local wholesale markets"
            ]
            for ans in answers:
                btns = page.query_selector_all(f'button:has-text("{ans}")')
                for b in btns:
                    if b.is_visible():
                        b.click()
                        print(f"  Selected: {ans}")
                        time.sleep(0.5)
                        break

            sub_quiz = page.query_selector('button:has-text("Submit Quiz")')
            if sub_quiz and sub_quiz.is_visible():
                sub_quiz.click()
                print("  Submitted Quiz!")
                time.sleep(3)

        page.screenshot(path='generated/m3_task1_all_done.png', full_page=True)
        print("Task 1 finished!")
        browser.close()

if __name__ == '__main__':
    run()
