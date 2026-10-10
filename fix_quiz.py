with open('super_runner.py', 'r') as f:
    code = f.read()

# 1. Swap the order of Section 1 and Section 2
# So that Quiz detection runs BEFORE AI Evaluation score check.
# This prevents the script from skipping a quiz because a previous AI evaluation score is still on the screen.

import re

# Find section 1
sec1_start = code.find('                # 1. Retry button')
sec2_start = code.find('                # 2. Quiz detection')
sec3_start = code.find('                # 3. Text activity')

if sec1_start != -1 and sec2_start != -1 and sec3_start != -1:
    section1_block = code[sec1_start:sec2_start]
    section2_block = code[sec2_start:sec3_start]
    
    # Swap them
    new_code = code[:sec1_start] + section2_block + section1_block + code[sec3_start:]
    code = new_code
    print("Swapped Section 1 and Section 2.")

# 2. Fix handle_quiz fallback logic
old_fallback = r'''      # 3. Fallback: ensure every question has a selection
      if not is_submit_ready():
          print("  [>] Fallback: clicking random options...")
          import random
          options = page.locator('div[role="radio"], label, input[type="radio"]')
          count = options.count()
          if count > 0:
              indices = list(range(count))
              random.shuffle(indices)
              for i in indices:
                  opt = options.nth(i)
                  try:
                      if opt.is_visible():
                          opt.scroll_into_view_if_needed()
                          opt.click(force=True)
                          time.sleep(0.15)
                  except Exception:
                      pass'''

new_fallback = r'''      # 3. Fallback: ensure every question has a selection
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
              # Click every single radio button on the page sequentially.
              # Since radio buttons in the same group deselect others, 
              # the final state will be the last option selected for each question.
              # This guarantees 100% completion of the quiz form.
              for i in range(count):
                  opt = options.nth(i)
                  try:
                      opt.scroll_into_view_if_needed()
                      opt.click(force=True)
                      time.sleep(0.1)
                  except Exception:
                      pass
          else:
              # If no actual radio inputs, try generic labels
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
                          pass'''

code = code.replace(old_fallback, new_fallback)

# 3. Completely revert Section 6 to the old "See All Tasks" logic, as the user requested "drop the test logic and remain on refresh logic".
# My previous revert accidentally left the start_act.click() in Section 6. Let's remove it.
old_sec6 = r'''                # 6. Inside a Task: check left sidebar for incomplete activities
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

                    print("[INFO] Returning to tasks list via 'See All Tasks'...")'''

new_sec6 = r'''                # 6. Inside a Task: check left sidebar for incomplete activities
                see_all = page.locator('button:has-text("See All Tasks")').first
                if see_all.count() > 0:
                    print("[INFO] Returning to tasks list via 'See All Tasks'...")'''

code = code.replace(old_sec6, new_sec6)

with open('super_runner.py', 'w') as f:
    f.write(code)

print("Updated handle_quiz and main loop successfully.")
