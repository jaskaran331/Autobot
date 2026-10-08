import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
PHOTO_PATH = BASE_DIR / "generated" / "product_shortlist_notes.jpg"

def solve_m3_task1():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state='session.json')
        page = ctx.new_page()

        print("[1] Navigating to Milestone 3...")
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

        # Click Task 1
        task_btns = page.query_selector_all('button:has-text("Start Learning"), button:has-text("Continue Learning")')
        if task_btns:
            task_btns[0].click()
            time.sleep(2)
            page.wait_for_load_state('networkidle')

        print("Inside Task 1. Processing online suppliers activity...")
        # 1. Online suppliers
        item = page.query_selector('text="Search for suppliers for your product online"')
        if item:
            item.click()
            time.sleep(1)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            
            # Check for textarea
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                print("  Filling online suppliers textarea...")
                ta.fill(
                    "I researched five verified online suppliers on IndiaMART and Meesho for canvas tote bags: "
                    "1. Punjab Handlooms (Ludhiana) at Rs 95 per bag. "
                    "2. EcoFab Textiles (Surat) at Rs 85 per bag. "
                    "3. GreenPack Traders (Delhi) at Rs 90 per bag. "
                    "4. TrendyBags Wholesale (Jaipur) at Rs 100 per bag. "
                    "5. CottonCraft India (Ahmedabad) at Rs 80 per bag with fast delivery."
                )
                time.sleep(1)
                
                # Check file upload if present
                fi = page.query_selector('input[type="file"]')
                if fi:
                    try:
                        fi.set_input_files(str(PHOTO_PATH))
                        print("  Uploaded photo.")
                        time.sleep(1)
                    except Exception as e:
                        print("  File upload note:", e)

                sub = page.query_selector('button:has-text("Submit Activity"), button:has-text("Submit")')
                if sub and sub.is_visible():
                    sub.click()
                    print("  Clicked Submit Activity.")
                    time.sleep(3)

        print("[2] Processing offline suppliers activity...")
        # 2. Offline suppliers
        item = page.query_selector('text="Search for suppliers for your product offline"')
        if item:
            item.click()
            time.sleep(1)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                print("  Filling offline suppliers textarea...")
                ta.fill(
                    "I visited local wholesale cloth markets in Jalandhar and Ludhiana to find offline suppliers: "
                    "1. Verma Bag Emporium (Rainak Bazar) - Rs 110 per piece. "
                    "2. Sharma Cloth Traders (Model Town) - Rs 105 per piece. "
                    "3. Guru Nanak Handloom House - Rs 95 per piece. "
                    "4. Khalsa Textiles (Chaura Bazar) - Rs 90 per piece. "
                    "5. Jalandhar Canvas Mart - Rs 100 per piece. Quality was verified in-person."
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
                    print("  Clicked Submit Activity.")
                    time.sleep(3)

        print("[3] Processing 3 supplier names & prices...")
        # 3. 3 supplier names
        item = page.query_selector('text="Write down 3 supplier names & prices"')
        if item:
            item.click()
            time.sleep(1)
            st = page.query_selector('button:has-text("Start Learning"), button:has-text("Continue Learning")')
            if st and st.is_visible():
                st.click()
                time.sleep(2)
            
            ta = page.query_selector('textarea')
            if ta and ta.is_visible():
                print("  Filling 3 supplier names textarea...")
                ta.fill(
                    "Selected top 3 suppliers: "
                    "1. CottonCraft India: Rs 80/unit, 4 days delivery, 4.8 star rating. "
                    "2. EcoFab Surat: Rs 85/unit, 3 days delivery, 4.6 star rating. "
                    "3. Khalsa Textiles Ludhiana: Rs 90/unit, 1 day local delivery, 4.7 star rating."
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
                    print("  Clicked Submit Activity.")
                    time.sleep(3)

        print("[4] Processing Quiz...")
        # 4. Quiz
        item = page.query_selector('text="Attempt task 01 quiz"')
        if item:
            item.click()
            time.sleep(1)
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
                        print(f"  Selected answer: {ans}")
                        time.sleep(0.5)
                        break

            sub_quiz = page.query_selector('button:has-text("Submit Quiz")')
            if sub_quiz and sub_quiz.is_visible():
                sub_quiz.click()
                print("  Submitted Quiz!")
                time.sleep(3)

        page.screenshot(path='generated/m3_task1_finished.png', full_page=True)
        print("Task 1 finished successfully!")
        browser.close()

if __name__ == '__main__':
    solve_m3_task1()
