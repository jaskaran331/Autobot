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
        for i in range(sem_blocks.count()):
            block = sem_blocks.nth(i)
            print(f"Block {i} is_visible(): {block.is_visible()}")
            if block.is_visible():
                text = block.inner_text()
                print(f"Block {i} text: {text[:50]!r}")
                if re.search(r"Semester\s+\d+", text, re.IGNORECASE):
                    print(f" -> MATCHED regex!")
                else:
                    print(f" -> DID NOT MATCH regex")
        
        # What if we use a different locator?
        print("\nChecking other locators:")
        alt_blocks = page.locator('p:text-matches("Semester \\\\d+", "i")')
        print(f"alt_blocks.count() = {alt_blocks.count()}")
        
        browser.close()

if __name__ == "__main__":
    main()
