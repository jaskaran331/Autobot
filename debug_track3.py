import os
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
        for _ in range(4):
            blocks = page.locator('div.rounded-2xl.bg-white')
            if blocks.count() > 0:
                try:
                    blocks.last.scroll_into_view_if_needed()
                except Exception:
                    pass
            page.wait_for_timeout(1000)
            
        print("Evaluating JS...")
        result = page.evaluate("""() => {
            const blocks = document.querySelectorAll('div.rounded-2xl.bg-white');
            let res = [];
            for (let block of blocks) {
                let text = block.innerText;
                let has_sem = /Semester\s+\d+/i.test(text);
                let has_100 = text.includes("100%");
                let btn = block.querySelector('button');
                res.push({
                    text_start: text.substring(0, 30),
                    has_sem: has_sem,
                    has_100: has_100,
                    has_btn: !!btn,
                    btn_text: btn ? btn.innerText : null
                });
            }
            return res;
        }""")
        
        print("JS Result:", result)
        browser.close()

if __name__ == "__main__":
    main()
