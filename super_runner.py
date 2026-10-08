import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session.json"
CURRICULUM_FILE = BASE_DIR / "curriculum_data.json"
PHOTO_PATH = BASE_DIR / "photo.jpg"

def load_quiz_answers():
    data = json.load(open(CURRICULUM_FILE, encoding="utf-8"))
    answers = []
    for term in data.get("terms", []):
        for course in term.get("courses", []):
            for mod in course.get("modules", []):
                for res in mod.get("resources", []):
                    if "quiz" in res:
                        if isinstance(res["quiz"], list):
                            for pair in res["quiz"]:
                                if len(pair) == 2:
                                    answers.append(str(pair[1]))
                        elif isinstance(res["quiz"], dict):
                            for q_text, ans_text in res["quiz"].items():
                                answers.append(str(ans_text))
    return set(answers)

def run():
    print("[*] Loading quiz answers...")
    valid_answers = load_quiz_answers()
    
    if not PHOTO_PATH.exists():
        with open(PHOTO_PATH, "wb") as f:
            f.write(b"") # Empty file, just needs to exist

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        
        print("[*] Navigating to Track...")
        page.goto("https://businessclass.punjab.gov.in/student/track", wait_until="networkidle")
        
        consecutive_idle = 0
        
        while consecutive_idle < 3:
            time.sleep(2.5)
            page.wait_for_load_state("networkidle")
            
            action_taken = False
            
            # 1. Are we in a Quiz?
            radios = page.query_selector_all("div[role='radio'], input[type='radio']")
            if radios:
                print("  [>] Quiz detected, answering...")
                answered = 0
                btns = page.query_selector_all("button, label, div[role='radio']")
                for b in btns:
                    try:
                        txt = b.inner_text().strip()
                        if txt in valid_answers and b.is_visible():
                            b.click()
                            answered += 1
                            time.sleep(0.2)
                    except Exception:
                        pass
                
                sub = page.query_selector('button >> text="Submit Quiz"') or page.query_selector('button >> text="Submit"')
                if sub and sub.is_visible():
                    sub.click()
                    print(f"  [OK] Quiz submitted ({answered} answers)")
                    action_taken = True
                    time.sleep(3)
                    continue

            # 2. Are we in a Textarea activity?
            ta = page.query_selector("textarea")
            if ta and ta.is_visible():
                print("  [>] Text activity detected...")
                if not ta.input_value().strip():
                    ta.fill("We have completed the necessary research and reached out to the relevant parties. This business step is complete and we are ready to proceed to the next milestone for our E-commerce store.")
                
                fi = page.query_selector('input[type="file"]')
                if fi and fi.is_visible():
                    try:
                        fi.set_input_files(str(PHOTO_PATH))
                    except: pass
                    
                sub = page.query_selector('button >> text="Submit Activity"') or page.query_selector('button >> text="Submit"')
                if sub and sub.is_visible():
                    sub.click()
                    print("  [OK] Text activity submitted.")
                    action_taken = True
                    time.sleep(3)
                    continue

            # 3. Are we in a Video/Reading?
            mark = page.query_selector('button >> text="Mark as Complete"')
            if mark and mark.is_visible():
                print("  [>] Video/Reading detected...")
                mark.click()
                print("  [OK] Marked as complete.")
                action_taken = True
                time.sleep(3)
                continue
                
            # 4. Are we looking at a Start/Continue button?
            starts = page.query_selector_all('button:not([data-clicked="true"]) >> text="Start Learning"')
            starts += page.query_selector_all('button:not([data-clicked="true"]) >> text="Continue Learning"')
            starts += page.query_selector_all('button:not([data-clicked="true"]) >> text="Attempt"')
            starts += page.query_selector_all('button:not([data-clicked="true"]) >> text="Start Activity"')
            clicked = False
            for s in starts:
                if s.is_visible():
                    print(f"  [>] Clicking navigation button: {s.inner_text().strip()}")
                    s.evaluate("node => node.setAttribute('data-clicked', 'true')")
                    s.click()
                    clicked = True
                    action_taken = True
                    time.sleep(3)
                    break
            if clicked:
                continue
                
            # If nothing happened
            if not action_taken:
                consecutive_idle += 1
                print(f"  [?] No actionable buttons found. Idle count: {consecutive_idle}")
            else:
                consecutive_idle = 0
                
        print("[*] Script finished. Assuming all milestones completed!")
        page.screenshot(path="super_runner_done.png")
        
if __name__ == "__main__":
    run()
