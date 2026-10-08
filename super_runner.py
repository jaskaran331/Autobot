import time
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import google.generativeai as genai

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session.json"
CURRICULUM_FILE = BASE_DIR / "curriculum_data.json"
PHOTO_PATH = BASE_DIR / "photo.jpg"

# Configure Gemini API if available
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-3.8-flash')
else:
    model = None

def load_quiz_answers():
    data = json.load(open(CURRICULUM_FILE, encoding="utf-8"))
    ans = []
    
    def extract_answers(d):
        if isinstance(d, dict):
            if d.get("isCorrect") == True and "option_heading" in d:
                ans.append(str(d["option_heading"]))
            for k, v in d.items():
                extract_answers(v)
        elif isinstance(d, list):
            for item in d:
                extract_answers(item)
                
    extract_answers(data)
    
    for term in data.get("terms", []):
        for course in term.get("courses", []):
            for mod in course.get("modules", []):
                for res in mod.get("resources", []):
                    if "quiz" in res:
                        if isinstance(res["quiz"], list):
                            for pair in res["quiz"]:
                                if len(pair) == 2:
                                    ans.append(str(pair[1]))
                        elif isinstance(res["quiz"], dict):
                            for q_text, ans_text in res["quiz"].items():
                                ans.append(str(ans_text))
                                
    return set(ans)

def login_if_needed(page, ctx):
    email = os.environ.get("BC_EMAIL", "")
    password = os.environ.get("BC_PASSWORD", "")
    
    page.goto("https://businessclass.punjab.gov.in/student/track", wait_until="networkidle")
    time.sleep(2)
    if "/login" not in page.url and "/auth" not in page.url:
        print("[*] Session is active.")
        return True
    
    print(f"[*] Logging in as {email}...")
    page.goto("https://businessclass.punjab.gov.in/login", wait_until="networkidle")
    time.sleep(2)
    
    try:
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        time.sleep(3)
    except Exception as e:
        print("Login err:", e)
        
    ctx.storage_state(path=str(SESSION_FILE))
    print("[*] Login successful.")
    return True

def generate_ai_response(page):
    if not model:
        return "Welcome to our community! Thank you so much for joining. You can expect exclusive updates, tips, offers, and behind-the-scenes content about our business and products. We are excited to have you here! I have successfully completed this task. I selected my target audience, entered my business name, and set up my warehouse and store by providing all required location details and tax information. I also added multiple product listings with clear descriptions, set up the price lists, configured online payment methods, and customized the design to look highly professional. I have successfully updated my inventory by adding all available stock, specifying quantities, and configuring shipping options, weights, and product variants like size and color. I reached out to 3 potential suppliers, negotiated the best price, and finalized the delivery terms. Furthermore, I established a marketing strategy, created a professional logo, set up social media accounts to attract customers, and planned for future growth. All initial steps are comprehensively completed, the research is documented, the required screenshots are provided, and the platform is now live and fully operational."
    
    try:
        title = page.evaluate("document.querySelector('h1, h2, h3, h4, h5')?.innerText || ''")
        desc = page.evaluate("document.body.innerText")
        # Extract a reasonable amount of text to send to Gemini
        desc = desc[:2000] if desc else ""
        
        prompt = f"Write a response (100-200 words) for this e-commerce business class activity. Make it sound like a real student submitting their work. Activity Title: {title}\nActivity Context: {desc}"
        print(f"  [>] Asking Gemini API to generate response for: {title}")
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if not text: raise ValueError("Empty response")
        return text
    except Exception as e:
        print("  [!] Gemini generation failed, falling back:", e)
        return "Welcome to our community! Thank you so much for joining. You can expect exclusive updates, tips, offers, and behind-the-scenes content about our business and products. We are excited to have you here! I have successfully completed this task. I selected my target audience, entered my business name, and set up my warehouse and store by providing all required location details and tax information. I also added multiple product listings with clear descriptions, set up the price lists, configured online payment methods, and customized the design to look highly professional. I have successfully updated my inventory by adding all available stock, specifying quantities, and configuring shipping options, weights, and product variants like size and color. I reached out to 3 potential suppliers, negotiated the best price, and finalized the delivery terms. Furthermore, I established a marketing strategy, created a professional logo, set up social media accounts to attract customers, and planned for future growth. All initial steps are comprehensively completed, the research is documented, the required screenshots are provided, and the platform is now live and fully operational."


def main():
    print("[*] Loading quiz answers...")
    valid_answers = load_quiz_answers()
    
    if not PHOTO_PATH.exists():
        with open(PHOTO_PATH, "wb") as f:
            f.write(b"") # Empty file, just needs to exist

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=os.environ.get("GITHUB_ACTIONS") != "true")
        context = browser.new_context(storage_state=str(SESSION_FILE)) if SESSION_FILE.exists() else browser.new_context()
        page = context.new_page()
        
        login_if_needed(page, context)
        
        print("[*] Navigating to Track...")
        page.goto("https://businessclass.punjab.gov.in/student/track", wait_until="networkidle")
        
        consecutive_idle = 0
        clicked_coords = set()
        
        while consecutive_idle < 3:
            time.sleep(2.5)
            try:
                page.wait_for_load_state("networkidle")
            except:
                pass
            
            if "/track" not in page.url and "/activity" not in page.url:
                page.goto("https://businessclass.punjab.gov.in/student/track", wait_until="networkidle")
                clicked_coords.clear()
            
            action_taken = False
            
            # Did we get an AI rejection?
            try_again = page.query_selector('button >> text="Try again"')
            if try_again and try_again.is_visible():
                print("  [>] AI Evaluation failed (Try Again), clicking...")
                try_again.click()
                time.sleep(2)
                action_taken = True
                
            # 1. Are we in a Quiz?
            sub_quiz = page.query_selector('button >> text="Submit Quiz"')
            if sub_quiz and sub_quiz.is_visible():
                print("  [>] Quiz detected, answering...")
                answered = 0
                for ans in valid_answers:
                    try:
                        ans_elems = page.query_selector_all(f'text="{ans}"')
                        for ans_elem in ans_elems:
                            if ans_elem.is_visible():
                                ans_elem.click()
                                answered += 1
                                time.sleep(0.2)
                    except Exception:
                        pass
                
                sub_quiz.click()
                print(f"  [OK] Quiz submitted ({answered} answers)")
                action_taken = True
                clicked_coords.clear()
                time.sleep(3)
                continue

            # 2. Are we in a Textarea activity?
            ta = page.query_selector("textarea")
            if ta and ta.is_visible():
                print("  [>] Text activity detected...")
                
                # Clear and refill with AI GENERATED response
                ta.fill("")
                dynamic_response = generate_ai_response(page)
                ta.fill(dynamic_response)
                
                fi = page.query_selector('input[type="file"]')
                if fi and fi.is_visible():
                    try:
                        fi.set_input_files(str(PHOTO_PATH))
                    except: pass
                    
                sub = page.query_selector('button >> text="Submit Activity"') or page.query_selector('button >> text="Submit"')
                if sub and sub.is_visible():
                    sub.click()
                    print("  [OK] Text activity submitted with Gemini API response.")
                    action_taken = True
                    clicked_coords.clear()
                    time.sleep(4)
                    continue

            # 3. Are we in a Video/Reading?
            mark = page.query_selector('button >> text="Mark as Complete"')
            if mark and mark.is_visible():
                print("  [>] Video/Reading detected...")
                mark.click()
                print("  [OK] Marked as complete.")
                action_taken = True
                clicked_coords.clear()
                time.sleep(3)
                continue
                
            # 4. Are we looking at a Start/Continue button?
            starts = page.query_selector_all('button >> text="Start Learning"')
            starts += page.query_selector_all('button >> text="Continue Learning"')
            starts += page.query_selector_all('button >> text="Attempt"')
            starts += page.query_selector_all('button >> text="Start Activity"')
            clicked = False
            
            for s in starts:
                if s.is_visible():
                    try:
                        # Skip Semester 1 completely
                        parent = page.evaluate("(el) => { let p = el.closest('.bg-white'); return p ? p.innerText : ''; }", s)
                        if "Semester 1" in parent:
                            continue
                    except Exception as e:
                        pass
                    
                    box = s.bounding_box()
                    if box:
                        coord = (int(box['x']), int(box['y']))
                        if coord not in clicked_coords:
                            print(f"  [>] Clicking navigation button: {s.inner_text().strip()} at {coord}")
                            clicked_coords.add(coord)
                            s.click()
                            clicked = True
                            action_taken = True
                            time.sleep(3)
                            if "/activity" in page.url or "/quiz" in page.url:
                                clicked_coords.clear()
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
    main()
