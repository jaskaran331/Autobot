import re

with open('super_runner.py', 'r') as f:
    code = f.read()

# REVERT SECTION 1
section1_old = r'''                    if score_match and int(score_match.group(1)) >= 70:
                        print(f"[INFO] Score is {score_match.group(1)} >= 70. Skipping 'Answer again' to move on.")
                        # Fall through to Step 6 (Next Activity)
                    else:'''
section1_new = r'''                    if score_match and int(score_match.group(1)) >= 70:
                        print(f"[INFO] Score is {score_match.group(1)} >= 70. Skipping 'Answer again' to move on.")
                        success_loops = page.evaluate("window.__success_loop_count || 0")
                        if success_loops >= 2:
                            print("[INFO] Completed 3 tasks without refresh. Reloading to sync sidebar state and prevent looping...")
                            page.evaluate("window.__success_loop_count = 0")
                            page.reload(wait_until="domcontentloaded")
                            page.wait_for_timeout(1000)
                        else:
                            page.evaluate(f"window.__success_loop_count = {success_loops + 1}")
                        # Fall through to Step 6 (Next Activity)
                    else:'''
code = code.replace(section1_old, section1_new)

# REVERT SECTION 5
section5_old = r'''                # 5. Quiz completion / "Great Job!" -> return to task list
                great_job = page.locator(':has-text("Great Job!"), :has-text("You passed"), :has-text("You Scored")').first
                if great_job.count() and great_job.is_visible():
                    print("[INFO] Activity/Quiz passed. Checking for next Start Learning button...")
                    
                    start_act = page.locator('button:has-text("Start Learning")').first
                    if start_act.count() and start_act.is_visible():
                        print("[INFO] Clicking next 'Start Learning' button directly without refreshing...")
                        start_act.scroll_into_view_if_needed()
                        start_act.click(force=True)
                        page.wait_for_timeout(1000)
                        action_taken = True
                        clicked_coords.clear()
                        continue

                    print("[INFO] No Start Learning button found. Returning to task list via 'See All Tasks'...")
                    see_all = page.locator('button:has-text("See All Tasks")').first
                    if see_all.count():
                        see_all.scroll_into_view_if_needed()
                        see_all.click()
                        page.wait_for_timeout(1000)
                        action_taken = True
                        clicked_coords.clear()
                        continue'''

section5_new = r'''                # 5. Quiz completion / "Great Job!" -> return to task list
                great_job = page.locator(':has-text("Great Job!"), :has-text("You passed"), :has-text("You Scored")').first
                if great_job.count() and great_job.is_visible():
                    print("[INFO] Activity/Quiz passed. Returning to task list...")
                    see_all = page.locator('button:has-text("See All Tasks")').first
                    if see_all.count():
                        see_all.scroll_into_view_if_needed()
                        
                        success_loops = page.evaluate("window.__success_loop_count || 0")
                        should_reload = (success_loops >= 2)
                        if should_reload:
                            print("[INFO] Completed 3 tasks. Reloading to sync milestone state...")
                            page.evaluate("window.__success_loop_count = 0")
                        else:
                            page.evaluate(f"window.__success_loop_count = {success_loops + 1}")
                            
                        see_all.click()
                        page.wait_for_timeout(1000)
                        
                        if should_reload:
                            page.reload(wait_until="domcontentloaded")
                            page.wait_for_timeout(1000)
                            
                        action_taken = True
                        clicked_coords.clear()
                        continue'''
code = code.replace(section5_old, section5_new)

# REVERT SECTION 6
section6_old = r'''                # 6. Inside a Task: check left sidebar for incomplete activities
                see_all = page.locator('button:has-text("See All Tasks")').first
                if see_all.count() > 0:
                    start_act = page.locator('button:has-text("Start Learning")').first
                    if start_act.count() and start_act.is_visible():
                        print("[INFO] Starting next activity in current task...")
                        start_act.scroll_into_view_if_needed()
                        start_act.click(force=True)
                        page.wait_for_timeout(1000)
                        action_taken = True
                        clicked_coords.clear()
                        continue

                    print("[INFO] No 'Start Learning' button found in sidebar. Returning to tasks list via 'See All Tasks'...")
                    see_all.scroll_into_view_if_needed()
                    see_all.click()
                    page.wait_for_timeout(1000)
                    action_taken = True
                    clicked_coords.clear()
                    continue'''

section6_new = r'''                # 6. Inside a Task: check left sidebar for incomplete activities
                see_all = page.locator('button:has-text("See All Tasks")').first
                if see_all.count() > 0:
                    start_act = page.locator('button:has-text("Start Learning")').first
                    if start_act.count() and start_act.is_visible():
                        print("[INFO] Starting next activity in current task...")
                        start_act.scroll_into_view_if_needed()
                        start_act.click(force=True)
                        page.wait_for_timeout(1000)
                        action_taken = True
                        clicked_coords.clear()
                        continue

                    print("[INFO] Returning to tasks list via 'See All Tasks'...")
                    see_all.scroll_into_view_if_needed()
                    
                    success_loops = page.evaluate("window.__success_loop_count || 0")
                    should_reload = (success_loops >= 2)
                    if should_reload:
                        print("[INFO] Reloading milestone list to sync completion state...")
                        page.evaluate("window.__success_loop_count = 0")
                    else:
                        page.evaluate(f"window.__success_loop_count = {success_loops + 1}")
                        
                    see_all.click()
                    page.wait_for_timeout(1000)
                    
                    if should_reload:
                        page.reload(wait_until="domcontentloaded")
                        page.wait_for_timeout(1000)
                        
                    action_taken = True
                    clicked_coords.clear()
                    continue'''
code = code.replace(section6_old, section6_new)

with open('super_runner.py', 'w') as f:
    f.write(code)

print("Reverted everything successfully!")
