import json
from pathlib import Path

curriculum_path = Path("knowledge_base/curriculum_microlearning.json")
with open(curriculum_path, "r", encoding="utf-8") as f:
    data = json.load(f)

output_dir = Path("knowledge_base/07_scenarios/microlearning")
output_dir.mkdir(parents=True, exist_ok=True)

for item in data["curriculum"]:
    topic_id = item["topic_id"].lower()
    title_slug = (
        item["title"]
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("&", "and")
        .replace("(", "")
        .replace(")", "")
    )
    filename = f"{topic_id}_{title_slug}.md"
    filepath = output_dir / filename

    vocab_lines = "\n".join(
        [f"- **{v['phrase']}**: {v['meaning']}" for v in item["vocabulary"]]
    )
    prompts_lines = "\n".join(
        [f"{idx+1}. \"{p}\"" for idx, p in enumerate(item["milo_prompts"])]
    )

    quiz_lines = []
    for q_idx, q in enumerate(item["quizzes"]):
        opts = " | ".join([f"{k}. {val}" for k, val in q["options"].items()])
        quiz_lines.append(
            f"**Question {q_idx+1} ({q['type']})**: {q['question']}\n- Options: {opts}\n- Correct Answer: **{q['answer']}**"
        )
    quizzes_text = "\n\n".join(quiz_lines)

    content = f"""---
topic_id: {item['topic_id']}
track_code: {item['track_code']}
track_name: {item['track_name']}
cefr_level: {item['cefr_level']}
duration_minutes: {item['duration_minutes']}
reference_source: \"{item['reference_source']}\"
---

# {item['title']} ({item['cefr_level']})

## Track: {item['track_name']}

### Can-Do Statement
{item['can_do_statement']}

### Briefing & Context
{item['briefing']}

### Target Vocabulary & Key Phrases
{vocab_lines}

### MILO Conversation Prompts (One-Question Flow)
{prompts_lines}

### Micro-Quiz
{quizzes_text}

### Academic Reference
{item['reference_source']}
"""
    filepath.write_text(content, encoding="utf-8")
    print(f"Generated: {filename}")

print("All 18 microlearning markdown files successfully generated!")
