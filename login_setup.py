"""
One-Time Session Setup:
Opens the browser on your screen, enters your email, and saves session.json once you log in.
After running this ONCE, agent.py will never ask for credentials again!
"""
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE_URL = "https://businessclass.punjab.gov.in"
BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "session.json"
STATUS_FILE = BASE_DIR / "login_completed.txt"
EMAIL = os.environ.get("BC_EMAIL", "")
PASSWORD = os.environ.get("BC_PASSWORD", "")

if not EMAIL:
    EMAIL = input("Enter your email (BC_EMAIL): ").strip()
if not PASSWORD:
    import getpass
    PASSWORD = getpass.getpass("Enter your password (BC_PASSWORD): ")

for i, arg in enumerate(sys.argv):
    if arg == "--password" and i + 1 < len(sys.argv):
        PASSWORD = sys.argv[i + 1]
    elif arg.startswith("--password="):
        PASSWORD = arg.split("=", 1)[1]


def main():
    print("\n" + "=" * 65, flush=True)
    print("   BUSINESS CLASS PUNJAB -- ONE-TIME LOGIN SETUP", flush=True)
    print("=" * 65 + "\n", flush=True)

    if STATUS_FILE.exists():
        STATUS_FILE.unlink()

    with sync_playwright() as pw:
        # Launch Chromium with normal GUI
        browser = pw.chromium.launch(
            headless=False,
            slow_mo=100,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()

        print(f"[...] Loading {SITE_URL}/login ...", flush=True)
        try:
            page.goto(f"{SITE_URL}/login", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_selector('input[type="email"]', timeout=15000)
        except Exception as e:
            print(f"[!] Warning while loading login page: {e}", flush=True)

        time.sleep(1)

        # Pre-fill email
        email_el = page.query_selector('input[type="email"]')
        if email_el:
            email_el.fill(EMAIL)
            print(f"[OK] Email auto-filled: {EMAIL}", flush=True)

        if PASSWORD:
            pw_el = page.query_selector('input[type="password"]')
            if pw_el:
                pw_el.fill(PASSWORD)
                time.sleep(0.5)
                btn = page.query_selector('button[type="submit"]')
                if btn:
                    print("[...] Submitting credentials automatically...", flush=True)
                    btn.click()
                else:
                    pw_el.press("Enter")
        else:
            print("\n" + "*" * 65, flush=True)
            print(">>> The browser window is now open on your screen!", flush=True)
            print(">>> Please type your password into the browser and click 'Log In'.", flush=True)
            print(">>> This script will detect your login and save your session automatically.", flush=True)
            print("*" * 65 + "\n", flush=True)

        # Monitor for navigation away from /login or dashboard elements
        start = time.time()
        logged_in = False
        last_logged_time = start

        while time.time() - start < 600:
            time.sleep(2)
            try:
                cur_url = page.url
            except Exception:
                print("\n[!] Browser window was closed.", flush=True)
                break

            if "/login" not in cur_url and cur_url != f"{SITE_URL}/login":
                print(f"\n[OK] Detected navigation away from /login: {cur_url}", flush=True)
                logged_in = True
                break

            try:
                if page.query_selector('nav, [class*="dashboard"], [class*="sidebar"], [class*="profile"]'):
                    print(f"\n[OK] Detected dashboard UI element on page: {cur_url}", flush=True)
                    logged_in = True
                    break
            except Exception:
                pass

            if time.time() - last_logged_time > 15:
                elapsed = int(time.time() - start)
                print(f"[...] Waiting for you to log in... ({elapsed}s elapsed)", flush=True)
                last_logged_time = time.time()

        if not logged_in:
            print("[!] Setup ended without successful login.", flush=True)
            browser.close()
            return

        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

        time.sleep(2)
        print(f"\n[OK] Login successful! Current page: {page.url}", flush=True)

        ctx.storage_state(path=str(SESSION_FILE))
        STATUS_FILE.write_text("SUCCESS", encoding="utf-8")
        print(f"[OK] Login session saved to: {SESSION_FILE.resolve()}", flush=True)
        print("\n" + "=" * 65, flush=True)
        print("  SESSION SAVED SUCCESSFULLY!", flush=True)
        print("  You can now close this window.", flush=True)
        print("  The agent will run seamlessly in the background!", flush=True)
        print("=" * 65 + "\n", flush=True)
        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    main()
