import json

data = json.load(open('curriculum_data.json', encoding='utf-8'))
term = data['terms'][0]
print(f"Term: {term.get('name')}")
for c_idx, course in enumerate(term.get('courses', [])):
    print(f"\nMilestone {c_idx+1}: {course.get('name')}")
    for m_idx, mod in enumerate(course.get('modules', [])):
        print(f"  Task {m_idx+1}: {mod.get('name')}")
        for r_idx, res in enumerate(mod.get('resources', [])):
            has_quiz = 'quiz' in res and 'questions' in res['quiz']
            q_count = len(res['quiz']['questions']) if has_quiz else 0
            kind = f"QUIZ ({q_count} qs)" if has_quiz else "CONTENT"
            print(f"    Act {r_idx+1}: [{kind}] {res.get('name')}")
