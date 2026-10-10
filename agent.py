"""
Business Class Punjab — Module Completion Agent
================================================
Automates module/assignment completion on businessclass.punjab.gov.in.

Usage:
    set GEMINI_API_KEY=your_key_here
    python agent.py                  -- normal run
    python agent.py --calibrate      -- dump HTML for selector debugging
    python agent.py --status         -- show state.json summary

The agent will:
  1. Open a browser, fill your email, let you type password + click Log In
  2. Discover all modules and their completion status
  3. For each incomplete module: extract questions, generate answers/images
  4. Show you each answer for review before submitting
  5. Track progress in state.json to avoid duplicate submissions
"""

import json
import os
import sys
import time
import base64
import re
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SITE_URL = "https://businessclass.punjab.gov.in"
STATE_FILE = Path(__file__).parent / "state.json"
SESSION_FILE = Path(__file__).parent / "session.json"
GENERATED_DIR = Path(__file__).parent / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

EMAIL = os.environ.get("BC_EMAIL", "")
PASSWORD = os.environ.get("BC_PASSWORD", "")

# Check for --password in CLI args
for i, arg in enumerate(sys.argv):
    if arg == "--password" and i + 1 < len(sys.argv):
        PASSWORD = sys.argv[i + 1]
    elif arg.startswith("--password="):
        PASSWORD = arg.split("=", 1)[1]

HEADLESS = "--headless" in sys.argv or (bool(PASSWORD) and "--headed" not in sys.argv)

# Exact selectors derived from the actual site HTML (Next.js app)
SEL = {
    # Login
    "email": 'input[type="email"]',
    "password": 'input[type="password"]',
    "login_btn": 'button[type="submit"]',

    # Post-login: the site redirects away from /login on success
    # We detect login by URL change + presence of nav/sidebar

    # Dashboard — these need calibration after first login (run --calibrate)
    # ponytail: placeholder selectors, will be updated after we see the dashboard HTML
    "module_links": 'a[href*="/module"], a[href*="/lesson"], a[href*="/milestone"], a[href*="/week"]',
    "all_cards": '[class*="card"], [class*="module"], [class*="milestone"]',

    # Module page — question/task areas
    "text_inputs": 'textarea, input[type="text"]:not([type="email"]):not([type="password"]):not([name="search"])',
    "file_inputs": 'input[type="file"]',
    "submit_btn": 'button[type="submit"], button:has-text("Submit"), button:has-text("Save")',
}


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "errors": {}, "last_run": None}


def save_state(state):
    state["last_run"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
_gemini_client = None

def gemini():
    global _gemini_client
    if _gemini_client:
        return _gemini_client
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        try:
            api_key = input("Enter your Gemini API key (GEMINI_API_KEY): ").strip()
        except EOFError:
            raise RuntimeError("GEMINI_API_KEY environment variable is missing.")
        os.environ["GEMINI_API_KEY"] = api_key
    from google import genai
    _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client



def gen_answer(question, context=""):
    prompt = (
        f"You are a student completing the Punjab Entrepreneurship Mindset Programme. "
        f"Answer this assignment question clearly and practically (150-300 words). "
        f"Focus on real business applications.\n\n"
        f"Module: {context}\nQuestion: {question}\n\nAnswer:"
    )
    try:
        r = gemini().models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        return r.text.strip()
    except Exception as e:
        print(f"  [!] Text gen failed: {e}")
        return None


def gen_image(description, path):
    prompt = (
        f"Create a clean, professional image for a business assignment: {description}. "
        f"Suitable for academic submission. No text overlays."
    )
    try:
        interaction = gemini().interactions.create(model="gemini-nano-banana-2.1", input=prompt)
        if interaction.output_image and interaction.output_image.data:
            Path(path).write_bytes(base64.b64decode(interaction.output_image.data))
            print(f"  [OK] Image: {path}")
            return str(path)
        print("  [!] Gemini returned no image")
    except Exception as e:
        print(f"  [!] Image gen failed: {e}")
    # Fallback: Pillow placeholder
    return _placeholder(description, path)


def _placeholder(text, path):
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (800, 600), "white")
        d = ImageDraw.Draw(img)
        y = 50
        for i in range(0, len(text), 60):
            d.text((50, y), text[i:i+60], fill="black")
            y += 25
        d.text((50, y + 30), "[placeholder - Gemini image failed]", fill="gray")
        img.save(path)
        return str(path)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Page helpers
# ---------------------------------------------------------------------------
def dump(page, name):
    hp = GENERATED_DIR / f"{name}.html"
    sp = GENERATED_DIR / f"{name}.png"
    hp.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(sp), full_page=True)
    print(f"  [i] Dumped: {hp.name}, {sp.name}")


def wait_for_login(page, timeout_sec=300):
    """Wait up to 5 minutes for user to complete login."""
    login_url = page.url
    start = time.time()
    while time.time() - start < timeout_sec:
        time.sleep(2)
        cur = page.url
        # SPA navigation: URL changes from /login to something else
        if "/login" not in cur and cur != login_url:
            time.sleep(3)
            return True
        # Also check if dashboard elements appeared (SPA might not change URL path)
        if page.query_selector('nav, [class*="sidebar"], [class*="dashboard"]'):
            time.sleep(2)
            return True
    return False


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def do_login(page, ctx):
    global EMAIL, PASSWORD
    
    # Prompt for credentials if not provided
    if not EMAIL:
        try:
            EMAIL = input("Enter your email (or set BC_EMAIL): ").strip()
        except EOFError:
            raise RuntimeError("BC_EMAIL environment variable is missing.")
            
    if not PASSWORD:
        import getpass
        print("If you do not enter a password now, you will need to type it in the browser.")
        try:
            PASSWORD = getpass.getpass("Enter your password (or set BC_PASSWORD, leave empty to type in browser): ")
        except EOFError:
            raise RuntimeError("BC_PASSWORD environment variable is missing.")

    print(f"\n[...] Checking session on {SITE_URL}")
    page.goto(SITE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # Check if already authenticated via session.json
    if "/login" not in page.url and page.query_selector('nav, [class*="sidebar"], [class*="dashboard"]'):
        print(f"[OK] Already authenticated! Active URL: {page.url}")
        dump(page, "dashboard")
        return

    print(f"\n[...] Navigating to {SITE_URL}/login")
    page.goto(f"{SITE_URL}/login", wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # Fill email automatically
    email_el = page.query_selector(SEL["email"])
    if email_el:
        email_el.fill(EMAIL)
        print(f"[OK] Email filled: {EMAIL}")
    else:
        print("[!] Email input not found!")
        dump(page, "login_error")
        sys.exit(1)

    # If password is provided in env var or args, enter it automatically
    if PASSWORD:
        print("[...] Password provided. Entering password...")
        pw_el = page.query_selector(SEL["password"])
        if pw_el:
            pw_el.fill(PASSWORD)
            time.sleep(0.5)
            login_btn = page.query_selector(SEL["login_btn"])
            if login_btn:
                print("[...] Clicking Log In...")
                login_btn.click()
            else:
                pw_el.press("Enter")
        else:
            print("[!] Password field not found!")
    else:
        print()
        print("=" * 60)
        print("  Now TYPE YOUR PASSWORD in the browser and click 'Log In'.")
        print("  (Tip: You can set $env:BC_PASSWORD=\"yourpass\" or pass --password)")
        print("  I'll wait up to 5 minutes.")
        print("=" * 60)
        print()

    if not wait_for_login(page):
        print("[!] Login timed out (5 min). Exiting.")
        dump(page, "login_timeout")
        sys.exit(1)

    page.wait_for_load_state("networkidle", timeout=15000)
    print(f"[OK] Logged in! URL: {page.url}")

    # Save session storage state so credentials are never needed again
    try:
        ctx.storage_state(path=str(SESSION_FILE))
        print(f"[OK] Saved persistent login session to {SESSION_FILE.name}")
    except Exception as e:
        print(f"[*] Warning: Could not save session state: {e}")

    dump(page, "dashboard")


# ---------------------------------------------------------------------------
# Module discovery
# ---------------------------------------------------------------------------
def discover_modules(page):
    print("\n[...] Discovering modules...")
    time.sleep(3)

    # Strategy: find all links and cards, catalog everything
    all_links = page.query_selector_all("a[href]")
    modules = []
    seen_hrefs = set()

    for link in all_links:
        href = link.get_attribute("href") or ""
        text = (link.inner_text() or "").strip()

        # Filter to likely module/lesson/milestone links
        if any(kw in href.lower() for kw in ["/module", "/lesson", "/milestone", "/week", "/assignment", "/quiz", "/task"]):
            if href not in seen_hrefs:
                seen_hrefs.add(href)
                mid = re.sub(r'\W+', '_', href.lower())[:60]
                modules.append({"id": mid, "title": text[:80] or href, "href": href})

    if not modules:
        # Fallback: look for card-like elements
        print("  [*] No module links found. Looking for card elements...")
        cards = page.query_selector_all(SEL["all_cards"])
        for i, card in enumerate(cards):
            text = (card.inner_text() or "").strip()[:80]
            if text and len(text) > 3:
                mid = re.sub(r'\W+', '_', text.lower())[:60]
                modules.append({"id": mid, "title": text, "href": "", "card_index": i})

    if not modules:
        print("  [!] No modules found at all.")
        print("  [i] Dumping page — you'll need to help me find the right selectors.")
        dump(page, "dashboard_no_modules")

        # Last resort: print ALL links so user can identify
        print("\n  All links on page:")
        for i, link in enumerate(all_links):
            text = (link.inner_text() or "").strip()[:50]
            href = link.get_attribute("href") or ""
            if text:
                print(f"    [{i:3d}] {text:50s} -> {href}")
        return modules

    print(f"[OK] Found {len(modules)} module(s):")
    for m in modules:
        print(f"  [ ] {m['title']}")

    return modules


# ---------------------------------------------------------------------------
# Question extraction
# ---------------------------------------------------------------------------
def extract_questions(page):
    time.sleep(2)
    questions = []

    # Gather all form inputs on the page
    text_els = page.query_selector_all(SEL["text_inputs"])
    file_els = page.query_selector_all(SEL["file_inputs"])

    if not text_els and not file_els:
        return questions  # No inputs found

    # Try to pair inputs with their labels/context
    # Strategy: for each input, walk up to find the nearest label or heading
    for i, el in enumerate(text_els):
        context = _get_input_context(page, el)
        questions.append({
            "index": i,
            "type": "text",
            "text": context,
            "selector_index": i,
        })

    for i, el in enumerate(file_els):
        context = _get_input_context(page, el)
        questions.append({
            "index": len(text_els) + i,
            "type": "file",
            "text": context,
            "selector_index": i,
        })

    return questions


def _get_input_context(page, el):
    """Try to find the question text associated with an input element."""
    # Try aria-label
    label = el.get_attribute("aria-label") or ""
    if label:
        return label

    # Try placeholder
    ph = el.get_attribute("placeholder") or ""

    # Try associated label via id
    el_id = el.get_attribute("id") or ""
    if el_id:
        label_el = page.query_selector(f'label[for="{el_id}"]')
        if label_el:
            return (label_el.inner_text() or "").strip()

    # Try parent's text content
    try:
        parent = el.evaluate_handle("el => el.parentElement")
        parent_text = parent.evaluate("el => el.innerText || ''")
        if parent_text and len(parent_text.strip()) > 5:
            return parent_text.strip()[:200]
    except Exception:
        pass

    # Try preceding sibling
    try:
        prev = el.evaluate_handle("el => el.previousElementSibling")
        prev_text = prev.evaluate("el => el.innerText || ''")
        if prev_text:
            return prev_text.strip()[:200]
    except Exception:
        pass

    return ph or "(no question text found)"


# ---------------------------------------------------------------------------
# Review & Submit
# ---------------------------------------------------------------------------
def review_item(q, answer, image_path, num, total):
    """Show generated content for one question. Returns (approved, final_answer)."""
    print(f"\n{'='*60}")
    print(f"  Question {num}/{total}")
    print(f"{'='*60}")
    print(f"  Q: {q['text'][:200]}")
    print(f"  Type: {q['type']}")

    if answer:
        print(f"\n  Generated Answer:")
        print(f"  {'-'*40}")
        for line in answer.split('\n'):
            print(f"    {line}")
        print(f"  {'-'*40}")

    if image_path:
        print(f"  Generated Image: {image_path}")

    print()
    while True:
        choice = input("  [A]pprove / [S]kip / [E]dit / [Q]uit > ").strip().lower()
        if choice == 'a':
            return True, answer
        elif choice == 's':
            return False, answer
        elif choice == 'e':
            print("  Type new answer (empty line to finish):")
            lines = []
            while True:
                line = input("    ")
                if not line:
                    break
                lines.append(line)
            answer = "\n".join(lines)
            print("  Updated. [A]pprove or [S]kip?")
        elif choice == 'q':
            sys.exit(0)


def submit_one(page, q, answer, image_path):
    """Fill and submit one question's answer."""
    try:
        if q["type"] == "text" and answer:
            els = page.query_selector_all(SEL["text_inputs"])
            if q["selector_index"] < len(els):
                els[q["selector_index"]].fill(answer)
                time.sleep(0.5)
                print(f"  [OK] Text filled")

        if q["type"] == "file" and image_path:
            els = page.query_selector_all(SEL["file_inputs"])
            if q["selector_index"] < len(els):
                els[q["selector_index"]].set_input_files(image_path)
                time.sleep(1)
                print(f"  [OK] File uploaded")

        return True
    except Exception as e:
        print(f"  [!] Fill error: {e}")
        return False


def submit_page(page):
    """Click the submit/save button on the current page."""
    btn = page.query_selector(SEL["submit_btn"])
    if btn:
        btn.click()
        time.sleep(3)
        print("  [OK] Submitted!")
        return True
    print("  [!] No submit button found — manual submit needed.")
    return False


# ---------------------------------------------------------------------------
# Calibrate mode
# ---------------------------------------------------------------------------
def calibrate(page):
    print("\n[CALIBRATE] Dumping dashboard structure...\n")
    dump(page, "cal_dashboard")

    # Print all links
    links = page.query_selector_all("a[href]")
    print(f"  Links: {len(links)}")
    for i, lnk in enumerate(links):
        t = (lnk.inner_text() or "").strip()[:50]
        h = lnk.get_attribute("href") or ""
        if t:
            print(f"    [{i:3d}] {t:50s} -> {h}")

    # Print interactive elements
    for sel_name in ['button', '[role="button"]', '[class*="card"]']:
        els = page.query_selector_all(sel_name)
        if els:
            print(f"\n  {sel_name}: {len(els)} found")
            for j, el in enumerate(els[:10]):
                print(f"    [{j}] {(el.inner_text() or '').strip()[:60]}")

    # Try navigating to first link
    first = None
    for sel in ["a[href*='module']", "a[href*='lesson']", "a[href*='milestone']",
                 "a[href*='week']", "a[href*='task']"]:
        first = page.query_selector(sel)
        if first:
            break

    if first:
        print(f"\n  Clicking first module link...")
        first.click()
        time.sleep(3)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        dump(page, "cal_first_module")

        # Form elements
        print("\n  Form elements on module page:")
        for sel in ['textarea', 'input[type="text"]', 'input[type="file"]',
                    'select', 'form', '[class*="upload"]']:
            els = page.query_selector_all(sel)
            if els:
                print(f"    {sel}: {len(els)}")

    print(f"\n[DONE] Check files in: {GENERATED_DIR.resolve()}")
    print("Update SEL dict in agent.py based on what you find.\n")
    input("Press Enter to close browser...")


# ---------------------------------------------------------------------------
# Status mode
# ---------------------------------------------------------------------------
def show_status():
    state = load_state()
    print(f"\nLast run: {state.get('last_run', 'never')}")
    print(f"Completed: {len(state['completed'])}")
    for mid, info in state["completed"].items():
        print(f"  [DONE] {info.get('title', mid)} ({info.get('completed_at', '?')})")
    if state["errors"]:
        print(f"\nErrors: {len(state['errors'])}")
        for mid, err in state["errors"].items():
            print(f"  [ERR]  {mid}: {err}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if "--status" in sys.argv:
        show_status()
        return

    state = load_state()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS, slow_mo=200)
        if SESSION_FILE.exists():
            try:
                ctx = browser.new_context(
                    storage_state=str(SESSION_FILE),
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )
                print(f"[OK] Loaded saved session from {SESSION_FILE.name}")
            except Exception as e:
                print(f"[*] Could not load session ({e}), creating fresh context.")
                ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        else:
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})

        page = ctx.new_page()

        # Login
        do_login(page, ctx)

        if "--calibrate" in sys.argv:
            calibrate(page)
            browser.close()
            return

        # Discover modules
        modules = discover_modules(page)
        if not modules:
            print("[!] No modules found. Try: python agent.py --calibrate")
            input("Press Enter to close...")
            browser.close()
            return

        # Filter already done
        pending = [m for m in modules if m["id"] not in state["completed"]]
        if not pending:
            print("\n[OK] All discovered modules already completed!")
            browser.close()
            return

        print(f"\n[...] {len(pending)} pending module(s).\n")

        for mi, mod in enumerate(pending, 1):
            print(f"\n{'#'*60}")
            print(f"  MODULE {mi}/{len(pending)}: {mod['title']}")
            print(f"{'#'*60}")

            # Navigate
            if mod.get("href"):
                url = mod["href"]
                if not url.startswith("http"):
                    url = SITE_URL.rstrip("/") + "/" + url.lstrip("/")
                page.goto(url, wait_until="networkidle", timeout=20000)
            elif "card_index" in mod:
                cards = page.query_selector_all(SEL["all_cards"])
                if mod["card_index"] < len(cards):
                    cards[mod["card_index"]].click()
                    time.sleep(3)

            time.sleep(2)
            dump(page, f"module_{mi}")

            # Extract questions
            questions = extract_questions(page)
            if not questions:
                print("  [*] No form inputs on this page.")
                print("  [*] This might be a reading/video module (no submission needed).")
                state["completed"][mod["id"]] = {
                    "title": mod["title"],
                    "completed_at": datetime.now().isoformat(),
                    "note": "No inputs found — likely reading/video only",
                }
                save_state(state)
                page.go_back()
                time.sleep(1)
                continue

            print(f"  [OK] {len(questions)} question(s) found")

            # Generate answers
            prepared = []
            for qi, q in enumerate(questions, 1):
                print(f"\n  [...] Generating for Q{qi}: {q['text'][:60]}...")
                answer = None
                img = None

                if q["type"] == "text":
                    answer = gen_answer(q["text"], context=mod["title"])
                elif q["type"] == "file":
                    img_path = GENERATED_DIR / f"mod{mi}_q{qi}.png"
                    img = gen_image(q["text"], img_path)

                prepared.append({"q": q, "answer": answer, "image": img})

            # Review each
            all_ok = True
            for qi, item in enumerate(prepared, 1):
                approved, final_answer = review_item(
                    item["q"], item["answer"], item["image"],
                    qi, len(prepared),
                )
                if approved:
                    item["answer"] = final_answer
                    submit_one(page, item["q"], item["answer"], item["image"])
                else:
                    all_ok = False

            # Submit the page
            if all_ok and prepared:
                submit_page(page)

            state["completed"][mod["id"]] = {
                "title": mod["title"],
                "completed_at": datetime.now().isoformat(),
                "questions": len(prepared),
            }
            save_state(state)
            print(f"\n  [OK] Module '{mod['title']}' done.")

            # Back to dashboard
            page.goto(page.url.split("/module")[0] or SITE_URL,
                       wait_until="networkidle", timeout=15000)
            time.sleep(2)

        # Summary
        print(f"\n{'='*60}")
        print(f"  DONE")
        print(f"{'='*60}")
        print(f"  Completed this run: {len(pending)}")
        print(f"  Total completed:    {len(state['completed'])}")
        if state["errors"]:
            print(f"  Errors:             {len(state['errors'])}")
            for mid, err in state["errors"].items():
                print(f"    - {mid}: {err}")
        print()
        browser.close()


if __name__ == "__main__":
    main()
