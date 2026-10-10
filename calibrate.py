"""
Calibration probe: dumps HTML+screenshots at each stage to map selectors.
Supports manual login or auto-login with BC_PASSWORD / --password.
Saves session state to session.json so you only log in once.

Usage:
    python calibrate.py
    python calibrate.py --password "your_password"
"""
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE_URL = "https://businessclass.punjab.gov.in"
OUT_DIR = Path(__file__).parent / "generated"
OUT_DIR.mkdir(exist_ok=True)
SESSION_FILE = Path(__file__).parent / "session.json"

EMAIL = os.environ.get("BC_EMAIL", "")
PASSWORD = os.environ.get("BC_PASSWORD", "")

if not EMAIL:
    EMAIL = input("Enter your email (BC_EMAIL): ").strip()
if not PASSWORD:
    import getpass
    PASSWORD = getpass.getpass("Enter your password (BC_PASSWORD): ")

HEADLESS = "--headless" in sys.argv or (bool(PASSWORD) and "--headed" not in sys.argv)

for i, arg in enumerate(sys.argv):
    if arg == "--password" and i + 1 < len(sys.argv):
        PASSWORD = sys.argv[i + 1]
    elif arg.startswith("--password="):
        PASSWORD = arg.split("=", 1)[1]


def dump(page, name):
    html_path = OUT_DIR / f"{name}.html"
    shot_path = OUT_DIR / f"{name}.png"
    html_path.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(shot_path), full_page=True)
    print(f"  [OK] Dumped: {html_path.name}")
    print(f"  [OK] Dumped: {shot_path.name}")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS, slow_mo=200)

        # Reuse session if available
        if SESSION_FILE.exists():
            try:
                ctx = browser.new_context(
                    storage_state=str(SESSION_FILE),
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )
                print(f"[OK] Loaded saved session from {SESSION_FILE.name}")
            except Exception:
                ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        else:
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})

        page = ctx.new_page()

        print("\n[1] Checking session / Loading site...")
        page.goto(SITE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        already_in = "/login" not in page.url and bool(page.query_selector('nav, [class*="dashboard"], [class*="sidebar"]'))

        if not already_in:
            if "/login" not in page.url:
                page.goto(f"{SITE_URL}/login", wait_until="networkidle", timeout=30000)
                time.sleep(2)

            dump(page, "01_login_page")

            # Fill email
            email_el = page.query_selector('input[type="email"]')
            if email_el:
                email_el.fill(EMAIL)
                print(f"  [OK] Email entered: {EMAIL}")

            # Fill password if provided
            if PASSWORD:
                pw_el = page.query_selector('input[type="password"]')
                if pw_el:
                    pw_el.fill(PASSWORD)
                    time.sleep(0.5)
                    btn = page.query_selector('button[type="submit"]')
                    if btn:
                        print("  [OK] Password entered. Clicking Log In...")
                        btn.click()
                    else:
                        pw_el.press("Enter")
            else:
                print("\n" + "=" * 60)
                print("  Type your password in the browser window and click Log In.")
                print("  (Or pass --password <pwd> or $env:BC_PASSWORD)")
                print("  Waiting up to 5 minutes...")
                print("=" * 60 + "\n")

            # Wait for login completion
            login_url = page.url
            start = time.time()
            logged_in = False
            while time.time() - start < 300:
                time.sleep(2)
                cur = page.url
                if "/login" not in cur and cur != login_url:
                    logged_in = True
                    break
                if page.query_selector('nav, [class*="dashboard"], [class*="sidebar"]'):
                    logged_in = True
                    break

            if not logged_in:
                print("  [!] Login timed out.")
                dump(page, "02_timeout")
                browser.close()
                return

            page.wait_for_load_state("networkidle", timeout=15000)
            try:
                ctx.storage_state(path=str(SESSION_FILE))
                print(f"  [OK] Session saved to {SESSION_FILE.name}")
            except Exception as e:
                print(f"  [*] Notice: could not save session: {e}")

        print(f"\n[2] Logged in! Active URL: {page.url}")
        dump(page, "03_dashboard")

        # Step 3: Catalog all links
        print("\n[3] Cataloging dashboard links:")
        links = page.query_selector_all("a[href]")
        for i, link in enumerate(links):
            text = (link.inner_text() or "").strip()[:50]
            href = link.get_attribute("href") or ""
            if text or any(k in href for k in ["module", "lesson", "milestone", "week", "task"]):
                print(f"  [{i:2d}] {text:45s} -> {href}")

        # Step 4: Catalog buttons / cards
        print("\n[4] Cards and buttons:")
        for sel in ['[class*="card"]', '[class*="module"]', '[class*="milestone"]', 'button']:
            els = page.query_selector_all(sel)
            if els:
                print(f"  Found {len(els)} elements for selector: {sel}")
                for j, el in enumerate(els[:5]):
                    t = (el.inner_text() or "").strip().replace("\n", " ")[:60]
                    if t:
                        print(f"    - {t}")

        # Step 5: Try navigating to first module link
        print("\n[5] Attempting to open first course module...")
        first_mod = None
        for sel in ["a[href*='module']", "a[href*='lesson']", "a[href*='milestone']", "a[href*='week']", "a[href*='task']"]:
            first_mod = page.query_selector(sel)
            if first_mod:
                print(f"  Found module element via: {sel}")
                break

        if first_mod:
            first_mod.click()
            time.sleep(3)
            page.wait_for_load_state("networkidle", timeout=15000)
            dump(page, "04_first_module")
            print(f"  Module URL: {page.url}")

            # Inspect form elements
            print("\n[6] Inputs / Questions in first module:")
            for inp_sel in ['textarea', 'input[type="text"]', 'input[type="file"]', 'select', 'button[type="submit"]']:
                els = page.query_selector_all(inp_sel)
                print(f"  {inp_sel}: {len(els)} found")

        print(f"\n{'='*60}")
        print(f"  Calibration Complete! Artifacts stored in: {OUT_DIR.resolve()}")
        print(f"{'='*60}\n")
        browser.close()


if __name__ == "__main__":
    main()
