import re

with open('super_runner.py', 'r') as f:
    code = f.read()

# Replace handle_quiz fallback
old_pattern = r'# 3\. Fallback: ensure every question has a selection.*?if is_submit_ready\(\):'
new_fallback = r'''# 3. Fallback: ensure every question has a selection
    if not is_submit_ready():
        print("  [>] Fallback: selecting one option per question...")
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)
        except Exception:
            pass
            
        options = page.locator('input[type="radio"]')
        count = options.count()
        if count > 0:
            for i in range(count):
                opt = options.nth(i)
                try:
                    opt.scroll_into_view_if_needed()
                    opt.click(force=True)
                    time.sleep(0.1)
                except Exception:
                    pass
        else:
            labels = page.locator('div[role="radio"], label')
            count = labels.count()
            if count > 0:
                for i in range(count):
                    opt = labels.nth(i)
                    try:
                        opt.scroll_into_view_if_needed()
                        opt.click(force=True)
                        time.sleep(0.1)
                    except Exception:
                        pass
                        
    page.wait_for_timeout(1000)
    if is_submit_ready():'''

code = re.sub(old_pattern, new_fallback, code, flags=re.DOTALL)

with open('super_runner.py', 'w') as f:
    f.write(code)

print("Replaced fallback.")
