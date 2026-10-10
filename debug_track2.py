import os
import re
from playwright.sync_api import sync_playwright

TRACK_URL = "https://businessclass.punjab.gov.in/student/track"
SESSION_FILE = "session.json"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto(TRACK_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        
        # Scroll logic
        for _ in range(3):
            blocks = page.locator('div.rounded-2xl.bg-white')
            if blocks.count() > 0:
                try:
                    blocks.last.scroll_into_view_if_needed()
                except Exception:
                    pass
            page.wait_for_timeout(1000)
            
        sem_blocks = page.locator('div.rounded-2xl.bg-white')
        print(f"sem_blocks.count() = {sem_blocks.count()}")
        
        expanded = False
        has_semester_blocks = False
        for i in range(sem_blocks.count()):
            block = sem_blocks.nth(i)
            text = block.inner_text()
            if re.search(r"Semester\s+\d+", text, re.IGNORECASE):
                has_semester_blocks = True
                print(f"\nBlock {i} text preview: {text[:40]!r}")
                print(f"Contains '100%': {'100%' in text}")
                if "100%" not in text:
                    btn = block.locator('button:has-text("Start Learning"), button:has-text("Continue Learning")').first
                    print(f"Incomplete semester! Button count: {btn.count()}")
                    if btn.count() > 0:
                        print(f"Button text: {btn.inner_text()!r}")
                        print(f"Button is_visible: {btn.is_visible()}")
                        print(f"Button bounding box: {btn.bounding_box()}")
        
        print(f"\nFinal State: has_sem={has_semester_blocks}, expanded={expanded}")
        browser.close()

if __name__ == "__main__":
    main()
