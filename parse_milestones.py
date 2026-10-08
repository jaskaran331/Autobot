import json

data = json.load(open('curriculum_data.json', encoding='utf-8'))
for t_idx, term in enumerate(data.get('terms', [])):
    print(f"Term {t_idx+1}: {term.get('name')}")
    for c_idx, course in enumerate(term.get('courses', [])):
        print(f"  Milestone {c_idx+1}: {course.get('name')}")
        for m_idx, mod in enumerate(course.get('modules', [])):
            print(f"    Task {m_idx+1}: {mod.get('name')}")
            for r_idx, res in enumerate(mod.get('resources', [])):
                r_type = res.get('resource_type') or ('quiz' if 'quiz' in res else 'unknown')
                print(f"      Act {r_idx+1}: [{r_type}] {res.get('name')}")
