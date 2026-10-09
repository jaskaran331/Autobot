import json
from pathlib import Path

curriculum_path = Path("curriculum_data.json")
data = json.loads(curriculum_path.read_text(encoding="utf-8"))

# We want a map of question_normalized -> list of correct option text
quiz_map = {}
all_correct_options = set()

def extract_quizzes(node):
    if isinstance(node, dict):
        if "quiz" in node and isinstance(node["quiz"], dict):
            q_data = node["quiz"]
            for q_item in q_data.get("questions", []):
                q_text = q_item.get("question", "").strip()
                if not q_text:
                    continue
                corrects = []
                for opt in q_item.get("options", []):
                    if opt.get("isCorrect"):
                        opt_heading = opt.get("option_heading", "").strip()
                        if opt_heading:
                            corrects.append(opt_heading)
                            all_correct_options.add(opt_heading)
                if corrects:
                    quiz_map[q_text] = corrects
        for k, v in node.items():
            extract_quizzes(v)
    elif isinstance(node, list):
        for item in node:
            extract_quizzes(item)

extract_quizzes(data)

# Also save quiz_answers.json
output_data = {
    "by_question": quiz_map,
    "all_correct": list(all_correct_options)
}
Path("quiz_answers.json").write_text(json.dumps(output_data, indent=2), encoding="utf-8")
print(f"Generated quiz_answers.json with {len(quiz_map)} questions and {len(all_correct_options)} unique correct answers.")
