import json

track = json.load(open('curriculum_data.json', encoding='utf-8'))
term1 = track['terms'][0]
print(f"Term 1: {term1['name']} ({len(term1['courses'])} milestones)")

for c_idx, course in enumerate(term1['courses']):
    print(f"\n==========================================")
    print(f"Milestone {c_idx+1}: {course['name']}")
    print(f"==========================================")
    for m_idx, module in enumerate(course['modules']):
        print(f"  Task {m_idx+1}: {module['name']}")
        for res in module.get('resources', []):
            r_type = res.get('type')
            r_title = res.get('name') or res.get('title')
            r_desc = res.get('description', '').replace('\n', ' ')
            print(f"    [{r_type}] {r_title}")
            if r_type == 'activity':
                print(f"      -> Prompt: {r_desc[:120]}")
