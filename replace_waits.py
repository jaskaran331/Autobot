with open('super_runner.py', 'r') as f:
    code = f.read()

# Make the scroll loop faster
code = code.replace(
'''                    # Scroll down by finding the last block and scrolling to it (triggers lazy loading)
                    for _ in range(4):
                        blocks = page.locator('div.rounded-2xl.bg-white')
                        if blocks.count() > 0:
                            try:
                                blocks.last.scroll_into_view_if_needed()
                            except Exception:
                                pass
                        page.wait_for_timeout(1000)''', 
'''                    # Scroll down by finding the last block and scrolling to it (triggers lazy loading)
                    for _ in range(4):
                        blocks = page.locator('div.rounded-2xl.bg-white')
                        if blocks.count() > 0:
                            try:
                                blocks.last.scroll_into_view_if_needed()
                            except Exception:
                                pass
                        page.wait_for_timeout(400)'''
)

code = code.replace(
'''                        if clicked_sem:
                            print("[INFO] Entering incomplete semester...")
                            page.wait_for_timeout(3000)
                            action_taken = True
                        else:
                            print("[INFO] Inside a completed semester or all semesters complete. Reloading to return to root Track page...")
                            page.reload(wait_until="domcontentloaded")
                            page.wait_for_timeout(3000)''',
'''                        if clicked_sem:
                            print("[INFO] Entering incomplete semester...")
                            page.wait_for_timeout(1000)
                            action_taken = True
                        else:
                            print("[INFO] Inside a completed semester or all semesters complete. Reloading to return to root Track page...")
                            page.reload(wait_until="domcontentloaded")
                            page.wait_for_timeout(1000)'''
)

with open('super_runner.py', 'w') as f:
    f.write(code)
