import os
from playwright.sync_api import sync_playwright
import json

TRACK_URL = "https://businessclass.punjab.gov.in/student/track"
SESSION_FILE = "session.json"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto(TRACK_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        # Dump the HTML of the main content
        html = page.evaluate('document.body.innerHTML')
        with open("track_dom_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Track DOM dumped to track_dom_dump.html")
        
        browser.close()

if __name__ == "__main__":
    main()
