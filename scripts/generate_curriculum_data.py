import json
from pathlib import Path

curriculum_path = Path("knowledge_base/curriculum_microlearning.json")
with open(curriculum_path, "r", encoding="utf-8") as f:
    data = json.load(f)

def enrich(vocab_list):
    vocab_items = []
    idiom_items = []
    for item in vocab_list:
        phrase = item.get("phrase", "").strip()
        meaning = item.get("meaning", "").strip()
        is_expression = (
            "..." in phrase
            or any(k in phrase.lower() for k in ["bucket list", "unwind", "batteries", "burnout", "initiative", "bottleneck", "drawback", "correlation", "hand", "unforeseen"])
        )
        clean_phrase = phrase.replace("...", "").strip()
        entry = {
            "phrase": phrase,
            "meaning": meaning,
            "example": f"Contoh: \"{clean_phrase}\" digunakan secara alami dalam percakapan."
        }
        if is_expression:
            idiom_items.append(entry)
        else:
            vocab_items.append(entry)
    if not vocab_items and idiom_items:
        half = len(idiom_items) // 2
        vocab_items = idiom_items[:half]
        idiom_items = idiom_items[half:]
    elif not idiom_items and vocab_items:
        half = len(vocab_items) // 2
        idiom_items = vocab_items[half:]
        vocab_items = vocab_items[:half]
    return vocab_items, idiom_items

topics_dict = {}
for top in data.get("curriculum", []):
    tid = top.get("topic_id", "").upper()
    v_items, i_items = enrich(top.get("vocabulary", []))
    topics_dict[tid] = {
        "topic_id": tid,
        "track_code": top.get("track_code", ""),
        "track_name": top.get("track_name", ""),
        "cefr_level": top.get("cefr_level", "B1"),
        "topic_number": top.get("topic_number", 1),
        "title": top.get("title", ""),
        "duration_minutes": top.get("duration_minutes", "3-5"),
        "can_do_statement": top.get("can_do_statement", ""),
        "briefing": top.get("briefing", ""),
        "vocabulary": v_items,
        "idioms": i_items,
        "milo_prompts": top.get("milo_prompts", []),
        "quizzes": top.get("quizzes", []),
        "reference_source": top.get("reference_source", "")
    }

js_content = f"""// MILO Master Curriculum Fallback Data (Generated from curriculum_microlearning.json)
// Ensures 100% offline and standalone reliability for all 18 microlearning modules.
window.MILO_CURRICULUM_DATA = {json.dumps(topics_dict, indent=2, ensure_ascii=False)};
"""

out_path = Path("frontend/js/curriculum-data.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(js_content)
print(f"Successfully generated {out_path} with {len(topics_dict)} topics!")
