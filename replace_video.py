with open('super_runner.py', 'r') as f:
    code = f.read()

video_logic = r'''
                # 3.5 Video player: watch until progress is >= 70%
                video_title = page.locator('h3.font-semibold.text-gray-900').first
                if video_title.count() and page.locator('div.h-2.bg-gray-200.rounded-full').count():
                    print("[INFO] Video content detected. Waiting until 70% progress...")
                    last_pct = -1
                    stuck_count = 0
                    while True:
                        import re
                        page_text = visible_text(page, 2000)
                        pct_match = re.search(r'(\d+)%', page_text)
                        
                        if pct_match:
                            pct = int(pct_match.group(1))
                            if pct != last_pct:
                                print(f"  [Video] Progress: {pct}%")
                                last_pct = pct
                                stuck_count = 0
                            else:
                                stuck_count += 1
                                
                            if pct >= 70:
                                print("[OK] Video reached 70%. Attempting to click Mark as Complete if present...")
                                mark = find_button(page, ["Mark as Complete"])
                                if mark:
                                    mark.click()
                                    page.wait_for_timeout(1000)
                                action_taken = True
                                break
                        else:
                            stuck_count += 1
                            
                        if stuck_count > 15:
                            print("[WARN] Video progress seems stuck or not found. Breaking loop.")
                            break
                            
                        page.wait_for_timeout(1000)
                    
                    if action_taken:
                        clicked_coords.clear()
                        continue
'''

if 'Video player: watch until progress' not in code:
    code = code.replace('                # 4. Mark as Complete', video_logic + '\n                # 4. Mark as Complete')
    with open('super_runner.py', 'w') as f:
        f.write(code)
    print('Video logic added back!')
else:
    print('Video logic already exists!')
