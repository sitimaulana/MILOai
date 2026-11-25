import os
import io
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer, JavascriptLexer, TextLexer
from pygments.formatters import ImageFormatter

os.makedirs("buku/screenshots", exist_ok=True)

def get_code_slice(filepath, start_line, end_line):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[start_line - 1 : end_line])

def render_vscode_card(code_text, lexer, title_text, output_path, line_start=1):
    formatter = ImageFormatter(
        style="monokai",
        font_name="Consolas",
        font_size=18,
        line_numbers=True,
        line_number_start=line_start,
        line_number_bg="#1E1E1E",
        line_number_fg="#858585",
        line_pad=6,
    )
    img_bytes = highlight(code_text, lexer, formatter)
    code_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    # Add VS Code dark window header & padding
    pad_x = 24
    pad_bottom = 24
    header_h = 44
    total_w = code_img.width + pad_x * 2
    total_h = code_img.height + header_h + pad_bottom

    canvas = Image.new("RGBA", (total_w, total_h), (30, 30, 30, 255))
    draw = ImageDraw.Draw(canvas)

    # Header bar
    draw.rectangle([0, 0, total_w, header_h], fill=(37, 37, 38, 255))
    draw.line([0, header_h, total_w, header_h], fill=(55, 55, 58, 255), width=1)

    # Window control dots (red, yellow, green)
    draw.ellipse([16, 15, 28, 27], fill=(255, 95, 86, 255))
    draw.ellipse([36, 15, 48, 27], fill=(255, 189, 46, 255))
    draw.ellipse([56, 15, 68, 27], fill=(39, 201, 63, 255))

    # Title text
    try:
        title_font = ImageFont.truetype("consola.ttf", 16)
    except Exception:
        title_font = ImageFont.load_default()
    draw.text((88, 13), title_text, fill=(204, 204, 204, 255), font=title_font)

    # Paste code image
    canvas.paste(code_img, (pad_x, header_h + 10))
    canvas.save(output_path, "PNG")
    print(f"Saved: {output_path} ({total_w}x{total_h})")

# 1. Gambar 3.10: Real Project Directory Tree
tree_text = """AI-MILO/
├── app/
│   ├── api/                # REST API endpoints (auth, chat, voice, feedback, placement)
│   ├── core/
│   │   ├── asr.py          # OpenAI Whisper-1 Speech-to-Text
│   │   ├── feedback.py     # Evaluasi Grammar, Vocabulary, & Fluency (JSON)
│   │   ├── llm.py          # GPT-4o-mini Tutor & Session Closing Protocol
│   │   ├── rag.py          # Adaptive Hybrid RAG (ChromaDB + BM25 + RRF)
│   │   └── tts.py          # OpenAI TTS-1 (Voice: nova)
│   ├── db/                 # SQLAlchemy Async ORM Models & Session
│   └── main.py             # Entry Point FastAPI Server (Port 8000)
├── frontend/
│   ├── assets/live2d/      # MILO Model (.moc3, .model3.json, .cdi3.json, textures)
│   ├── js/
│   │   ├── curriculum-data.js  # 18 Modul Microlearning CEFR B1-B2
│   │   ├── milo-live2d.js      # Real Audio Lip-Sync (Web Audio API AnalyserNode)
│   │   ├── practice.js         # Dual Mode Mic (Push-to-Talk & Smart VAD)
│   │   └── briefing.js / summary.js
│   └── *.html              # login, setup-level, dashboard, briefing, practice, summary
├── knowledge_base/         # Korpus Silabus CEFR B1-B2 & ingest.py
├── live2dmodel/            # Proyek Rigging Asli Live2D Cubism (.cmo3)
├── tests/                  # Unit Tests (test_live2d_assets.py, test_closing.py)
├── docker-compose.bifrost.yml  # Kontainer AI Gateway Bifrost (Port 8080)
└── pyproject.toml          # Manajemen Dependensi Python 3.11 via uv"""

render_vscode_card(
    tree_text,
    TextLexer(),
    "EXPLORER: AI-MILO (d:\\Kuliah\\PA\\AI-MILO)",
    "buku/screenshots/Gambar_3_10_Struktur_Direktori_VSCode.png",
    line_start=1,
)

# 2. Gambar 3.13: Real Audio Lip-Sync (milo-live2d.js)
code_313 = get_code_slice("frontend/js/milo-live2d.js", 611, 642)
render_vscode_card(
    code_313,
    JavascriptLexer(),
    "frontend/js/milo-live2d.js — Web Audio API Lip-Sync AnalyserNode",
    "buku/screenshots/Gambar_3_13_LipSync_milo_live2d.png",
    line_start=611,
)

# 3. Gambar 3.14: Audio Recording & VAD (practice.js)
code_314 = get_code_slice("frontend/js/practice.js", 538, 578)
render_vscode_card(
    code_314,
    JavascriptLexer(),
    "frontend/js/practice.js — startRecording() & MediaRecorder Setup",
    "buku/screenshots/Gambar_3_14_Recording_practice_js.png",
    line_start=538,
)

# 4. Gambar 3.16: Backend Closing Protocol (app/core/llm.py)
code_316 = get_code_slice("app/core/llm.py", 190, 244)
render_vscode_card(
    code_316,
    PythonLexer(),
    "app/core/llm.py — MiloLLM.generate() & Session Closing Protocol",
    "buku/screenshots/Gambar_3_16_Backend_Closing_llm_py.png",
    line_start=190,
)
