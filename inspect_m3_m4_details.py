import json

data = json.load(open('curriculum_data.json', encoding='utf-8'))
term = data['terms'][0]

for m_num in [3, 4]:
    course = term['courses'][m_num - 1]
    print(f"\n=================== MILESTONE {m_num}: {course['name']} ===================")
    for t_idx, mod in enumerate(course['modules']):
        print(f"\n--- Task {t_idx + 1}: {mod['name']} ---")
        for a_idx, res in enumerate(mod['resources']):
            name = res.get('name', '')
            desc = res.get('description', '')
            quiz = res.get('quiz')
            if quiz:
                print(f"  [QUIZ] {name} ({len(quiz['questions'])} questions)")
                for q in quiz['questions']:
                    q_text = q['question']
                    correct = [opt['option_heading'] for opt in q['options'] if opt.get('isCorrect')]
                    print(f"    Q: {q_text}")
                    print(f"       -> Correct: {correct[0] if correct else 'None'}")
            else:
                print(f"  [ACTIVITY] {name}")
                if desc:
                    print(f"    Info: {desc[:100]}...")
