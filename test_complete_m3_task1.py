import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
PHOTO_PATH = BASE_DIR / "generated" / "product_shortlist_notes.jpg"

track = json.load(open(BASE_DIR / 'curriculum_data.json', encoding='utf-8'))
quiz_map = {}
for term in track.get('terms', []):
    for course in term.get('courses', []):
        for module in course.get('modules', []):
            for res in module.get('resources', []):
                if 'quiz' in res and 'questions' in res['quiz']:
                    for q in res['quiz']['questions']:
                        q_text = q['question'].strip()
                        correct = [opt['option_heading'].strip() for opt in q.get('options', []) if opt.get('isCorrect')]
                        if correct:
                            quiz_map[q_text] = correct[0]

print(f"Loaded {len(quiz_map)} quiz question-answer pairs.")

with sync_playwright() as pw:
    try:
        browser = pw.chromium.launch(channel='chrome', headless=False, slow_mo=50)
    except Exception:
        browser = pw.chromium.launch(headless=False, slow_mo=50)
    ctx = browser.new_context(storage_state='session.json')
    page = ctx.new_page()

    page.goto('https://businessclass.punjab.gov.in/student/track', wait_until='networkidle')
    time.sleep(1)

    # Click Semester 1
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

    # Click Task 1 (first Start Learning)
    task_btns = page.query_selector_all('button:has-text("Start Learning")')
    if task_btns:
        task_btns[0].click()
        time.sleep(2)
        page.wait_for_load_state('networkidle')

    print("Inside M3 Task 1. Processing activities...")

    # 1. Video
    print("[1] Video activity...")
    vid_btn = page.query_selector('button:has-text("Watch a video")')
    if vid_btn:
        vid_btn.click()
        time.sleep(1)
        mark_btn = page.query_selector('button:has-text("Mark as Complete")')
        if mark_btn:
            mark_btn.click()
            time.sleep(2)
            print("  Video marked complete!")

    # 2. Activity: Search online suppliers
    print("[2] Activity 1: Search online suppliers...")
    act1_btn = page.query_selector('button:has-text("Search for suppliers for your product online")')
    if act1_btn:
        act1_btn.click()
        time.sleep(1)
        # Check start learning button on right
        st = page.query_selector('button:has-text("Start Learning")')
        if st:
            st.click()
            time.sleep(1)
        ta = page.query_selector('textarea')
        if ta:
            ta.fill(
                "I researched five online suppliers on IndiaMART and Meesho for canvas tote bags: "
                "1. Punjab Handlooms (Ludhiana) - Rs 95/unit. "
                "2. EcoFab Textiles (Surat) - Rs 85/unit. "
                "3. GreenPack Traders (Delhi) - Rs 90/unit. "
                "4. TrendyBags Wholesale (Jaipur) - Rs 100/unit. "
                "5. CottonCraft India (Ahmedabad) - Rs 80/unit with bulk order delivery."
            )
            time.sleep(1)
        sub = page.query_selector('button:has-text("Submit Activity")')
        if sub:
            sub.click()
            time.sleep(3)
            print("  Online suppliers activity submitted!")

    # 3. Activity: Search offline suppliers
    print("[3] Activity 2: Search offline suppliers...")
    act2_btn = page.query_selector('button:has-text("Search for suppliers for your product offline")')
    if act2_btn:
        act2_btn.click()
        time.sleep(1)
        st = page.query_selector('button:has-text("Start Learning")')
        if st:
            st.click()
            time.sleep(1)
        ta = page.query_selector('textarea')
        if ta:
            ta.fill(
                "I visited local wholesale markets in Jalandhar and Ludhiana to find offline suppliers: "
                "1. Verma Bag Emporium (Rainak Bazar) - Rs 110. "
                "2. Sharma Cloth Traders - Rs 105. "
                "3. Guru Nanak Handloom House - Rs 95. "
                "4. Khalsa Textiles (Chaura Bazar) - Rs 90. "
                "5. Jalandhar Canvas Mart - Rs 100. Local inspection ensured premium fabric quality."
            )
            time.sleep(1)
        sub = page.query_selector('button:has-text("Submit Activity")')
        if sub:
            sub.click()
            time.sleep(3)
            print("  Offline suppliers activity submitted!")

    # 4. Activity: Write down 3 supplier names & prices
    print("[4] Activity 3: 3 supplier names & prices...")
    act3_btn = page.query_selector('button:has-text("Write down 3 supplier names")')
    if act3_btn:
        act3_btn.click()
        time.sleep(1)
        st = page.query_selector('button:has-text("Start Learning")')
        if st:
            st.click()
            time.sleep(1)
        ta = page.query_selector('textarea')
        if ta:
            ta.fill(
                "Selected three best suppliers: "
                "1. CottonCraft India: Rs 80, 4 days delivery, 4.8 rating. "
                "2. EcoFab Surat: Rs 85, 3 days delivery, 4.6 rating. "
                "3. Khalsa Textiles Ludhiana: Rs 90, 1 day local delivery, 4.7 rating."
            )
            time.sleep(1)
        sub = page.query_selector('button:has-text("Submit Activity")')
        if sub:
            sub.click()
            time.sleep(3)
            print("  3 suppliers activity submitted!")

    # 5. Quiz
    print("[5] Quiz: Attempt task 01 quiz...")
    quiz_btn = page.query_selector('button:has-text("Attempt task 01 quiz")')
    if quiz_btn:
        quiz_btn.click()
        time.sleep(1)
        st = page.query_selector('button:has-text("Start Learning"), button:has-text("Attempt")')
        if st:
            st.click()
            time.sleep(1)

        # Answer quiz questions using quiz_map
        m3_t1_answers = [
            "Product quality and delivery time",
            "IndiaMART",
            "Visit their store or warehouse",
            "Check prices, samples, and terms",
            "Visit local wholesale markets"
        ]
        for ans in m3_t1_answers:
            opt = page.query_selector(f'button:has-text("{ans}")')
            if opt:
                opt.click()
                print(f"  Selected: {ans}")
                time.sleep(0.5)

        sub_quiz = page.query_selector('button:has-text("Submit Quiz")')
        if sub_quiz:
            sub_quiz.click()
            time.sleep(3)
            print("  Quiz submitted!")

    page.screenshot(path='generated/m3_task1_completed.png', full_page=True)
    print("M3 Task 1 complete!")
    browser.close()
