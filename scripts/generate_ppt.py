"""
Script to generate the 12-slide Progress Presentation PPTX for AI-MILO
Matching the exact template and structure of the PENS TRM presentation reference.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="AI_MILO_Presentasi_Progres_PA.pptx"):
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    # Color Palette
    BG_LIGHT = RGBColor(248, 250, 252)       # #F8FAFC
    PRIMARY_NAVY = RGBColor(30, 41, 59)      # #1E293B
    ACCENT_BLUE = RGBColor(37, 99, 235)      # #2563EB
    TEAL = RGBColor(13, 148, 136)            # #0D9488
    AMBER = RGBColor(217, 119, 6)            # #D97706
    CARD_BG = RGBColor(255, 255, 255)        # #FFFFFF
    CARD_BORDER = RGBColor(203, 213, 225)    # #CBD5E1
    CARD_BORDER_ACTIVE = RGBColor(59, 130, 246) # #3B82F6
    TEXT_MUTED = RGBColor(100, 116, 139)     # #64748B
    TEXT_DARK = RGBColor(15, 23, 42)         # #0F172A
    HEADER_BG = RGBColor(224, 242, 254)      # #E0F2FE (Soft Blue)
    PENS_BLUE = RGBColor(14, 116, 144)       # #0E7490

    def add_background_decor(slide, title_text=None, show_page_arrow=True):
        # Top banner / accent shape
        top_accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12)
        )
        top_accent.fill.solid()
        top_accent.fill.fore_color.rgb = ACCENT_BLUE
        top_accent.line.fill.background()

        # Department / College watermark tag (top right)
        logo_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.3), Inches(2.5), Inches(0.6))
        tf = logo_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        run = p.add_run()
        run.text = "PENS  |  TRM"
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = PENS_BLUE
        
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.RIGHT
        run2 = p2.add_run()
        run2.text = "Teknologi Rekayasa Multimedia"
        run2.font.size = Pt(9)
        run2.font.color.rgb = TEXT_MUTED

        # Slide Title if provided
        if title_text:
            tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.5), Inches(0.8))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = title_text
            run.font.bold = True
            run.font.size = Pt(28)
            run.font.color.rgb = PRIMARY_NAVY

        # Next page arrow button (bottom right) like template
        if show_page_arrow:
            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(12.3), Inches(6.5), Inches(0.6), Inches(0.6)
            )
            circle.fill.solid()
            circle.fill.fore_color.rgb = ACCENT_BLUE
            circle.line.fill.background()

            arrow = slide.shapes.add_textbox(Inches(12.3), Inches(6.45), Inches(0.6), Inches(0.6))
            p = arrow.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = "›"
            r.font.bold = True
            r.font.size = Pt(24)
            r.font.color.rgb = RGBColor(255, 255, 255)

    def add_card(slide, left, top, width, height, title, body_bullets, header_color=PRIMARY_NAVY, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        # Header box inside card
        header_h = Inches(0.45)
        hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, header_h)
        hdr.fill.solid()
        hdr.fill.fore_color.rgb = header_color
        hdr.line.fill.background()
        p = hdr.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title
        r.font.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(255, 255, 255)

        # Content text box
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + header_h + Inches(0.08), width - Inches(0.3), height - header_h - Inches(0.15))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(body_bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(4)
            r = p.add_run()
            r.text = bullet
            r.font.size = Pt(10.5)
            r.font.color.rgb = TEXT_DARK
        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background_decor(s1, show_page_arrow=True)

    # Diagonal aesthetic background accent (right side)
    triangle = s1.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE, Inches(8.5), Inches(0.12), Inches(4.833), Inches(7.38))
    triangle.fill.solid()
    triangle.fill.fore_color.rgb = RGBColor(224, 231, 255) # Soft Indigo/blue
    triangle.line.fill.background()
    triangle.rotation = 180

    # Project badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(2.8), Inches(0.6))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(238, 242, 255)
    badge.line.color.rgb = ACCENT_BLUE
    badge.line.width = Pt(1.2)
    p_badge = badge.text_frame.paragraphs[0]
    p_badge.alignment = PP_ALIGN.CENTER
    r_badge = p_badge.add_run()
    r_badge.text = "PROPOSAL & PROGRES PA"
    r_badge.font.bold = True
    r_badge.font.size = Pt(11)
    r_badge.font.color.rgb = ACCENT_BLUE

    # Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(8.0), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "Asisten Virtual Dua Dimensi (2D) Berbasis OpenAI\nUntuk Meningkatkan Keterlibatan Belajar\nBerbicara Bahasa Inggris"
    r1.font.bold = True
    r1.font.size = Pt(25)
    r1.font.color.rgb = PRIMARY_NAVY

    p1_sub = tf1.add_paragraph()
    p1_sub.space_before = Pt(8)
    r1_sub = p1_sub.add_run()
    r1_sub.text = "AI-MILO: Multimodal Interactive Learning Companion (CEFR B1–B2)"
    r1_sub.font.bold = True
    r1_sub.font.size = Pt(14)
    r1_sub.font.color.rgb = ACCENT_BLUE

    # Presenter & Supervisors Info Card
    info_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(7.8), Inches(2.5))
    info_card.fill.solid()
    info_card.fill.fore_color.rgb = CARD_BG
    info_card.line.color.rgb = CARD_BORDER
    info_card.line.width = Pt(1)

    tb_info = s1.shapes.add_textbox(Inches(1.0), Inches(4.4), Inches(7.4), Inches(2.3))
    tfi = tb_info.text_frame
    tfi.word_wrap = True

    p = tfi.paragraphs[0]
    r = p.add_run()
    r.text = "Disusun Oleh:"
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_MUTED

    p_pres = tfi.add_paragraph()
    r = p_pres.add_run()
    r.text = "Siti Maulana Shofiyah"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = PRIMARY_NAVY
    r2 = p_pres.add_run()
    r2.text = "  (NRP. 5323600043)"
    r2.font.size = Pt(12)
    r2.font.color.rgb = TEXT_MUTED

    p_sep = tfi.add_paragraph()
    p_sep.space_before = Pt(8)
    r = p_sep.add_run()
    r.text = "Dosen Pembimbing:"
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_MUTED

    # Two column supervisor info
    p_sup1 = tfi.add_paragraph()
    r = p_sup1.add_run()
    r.text = "1. Akhmad Alimudin, S.ST., M.Kom., Ph.D."
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY_NAVY
    r = p_sup1.add_run()
    r.text = " (NIP. 198612082014041002)"
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_MUTED

    p_sup2 = tfi.add_paragraph()
    r = p_sup2.add_run()
    r.text = "2. Rendra Suprobo Aji, S.T., M.T."
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY_NAVY
    r = p_sup2.add_run()
    r.text = " (NIP. 198705212023211023)"
    r.font.size = Pt(10)
    r.font.color.rgb = TEXT_MUTED

    # Add character image if present
    img_milo = "frontend/assets/milo_companion.png"
    if os.path.exists(img_milo):
        try:
            s1.shapes.add_picture(img_milo, Inches(9.2), Inches(1.2), width=Inches(2.8))
        except Exception as e:
            print("Error adding milo image on slide 1:", e)

    # ==========================================
    # SLIDE 2: MDLC METHODOLOGY
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background_decor(s2, title_text="MDLC Methodology")

    mdlc_steps = [
        ("1. Concept", ["Defines core objectives, target learners (CEFR B1-B2), problem domain (speaking anxiety), and persona design."], ACCENT_BLUE),
        ("2. Design", ["Designs system architecture, conversational dialogue scaffolding (One-Question Rule), user flow, & wireframe."], ACCENT_BLUE),
        ("3. Material Collecting", ["Curates CEFR syllabus knowledge base (Obsidian/ChromaDB), Live2D model assets, and voice TTS profiles."], ACCENT_BLUE),
        ("4. Assembly", ["Integrates Whisper ASR, ChromaDB RAG, GPT-4o-mini LLM, OpenAI TTS, & Live2D WebGL lip-sync in FastAPI."], TEAL),
        ("5. Testing", ["Conducts Black Box functional tests, DeepEval LLM benchmarks, and Usability/Engagement testing (UEQ, N-Gain)."], TEAL),
        ("6. Distribution", ["Deploys responsive web platform with microlearning session manager for accessible independent practice."], TEAL),
    ]

    # Row 1 (Steps 1, 2, 3)
    col_w = Inches(3.6)
    row_h = Inches(2.2)
    gap_x = Inches(0.4)
    y_r1 = Inches(1.6)
    y_r2 = Inches(4.3)

    for i in range(3):
        x = Inches(0.8) + i * (col_w + gap_x)
        title, bullets, color = mdlc_steps[i]
        add_card(s2, x, y_r1, col_w, row_h, title, bullets, header_color=color)

    # Row 2 (Steps 6, 5, 4 - reverse flow like snake / cycle)
    # Step 6 (Distribution)
    add_card(s2, Inches(0.8), y_r2, col_w, row_h, mdlc_steps[5][0], mdlc_steps[5][1], header_color=mdlc_steps[5][2])
    # Step 5 (Testing)
    add_card(s2, Inches(0.8) + col_w + gap_x, y_r2, col_w, row_h, mdlc_steps[4][0], mdlc_steps[4][1], header_color=mdlc_steps[4][2])
    # Step 4 (Assembly)
    add_card(s2, Inches(0.8) + 2 * (col_w + gap_x), y_r2, col_w, row_h, mdlc_steps[3][0], mdlc_steps[3][1], header_color=mdlc_steps[3][2])

    # Connective arrows
    # Row 1: 1 -> 2 -> 3
    for i in range(2):
        arr = s2.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(0.8) + (i+1)*col_w + i*gap_x + Inches(0.08), y_r1 + Inches(0.9), Inches(0.24), Inches(0.24))
        arr.fill.solid()
        arr.fill.fore_color.rgb = ACCENT_BLUE
        arr.line.fill.background()

    # Down from 3 to 4
    arr_down = s2.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(0.8) + 2*(col_w + gap_x) + Inches(1.6), y_r1 + row_h + Inches(0.12), Inches(0.24), Inches(0.24))
    arr_down.fill.solid()
    arr_down.fill.fore_color.rgb = TEAL
    arr_down.line.fill.background()

    # Row 2: 4 <- 5 <- 6
    for i in range(2):
        arr_left = s2.shapes.add_shape(MSO_SHAPE.LEFT_ARROW, Inches(0.8) + (2-i)*col_w + (2-i-1)*gap_x + Inches(0.08), y_r2 + Inches(0.9), Inches(0.24), Inches(0.24))
        arr_left.fill.solid()
        arr_left.fill.fore_color.rgb = TEAL
        arr_left.line.fill.background()

    # ==========================================
    # SLIDE 3: CONCEPT
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background_decor(s3, title_text="Concept")

    # Left Side: Character / Visual Illustration Box
    left_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.1))
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = RGBColor(238, 242, 255)
    left_box.line.color.rgb = RGBColor(199, 210, 254)
    left_box.line.width = Pt(1.5)

    img_gesture = "frontend/assets/milo_gesture.png"
    if os.path.exists(img_gesture):
        try:
            s3.shapes.add_picture(img_gesture, Inches(1.4), Inches(1.8), height=Inches(4.4))
        except Exception as e:
            print("Error adding gesture image on slide 3:", e)

    # Right Side: 3 Concept Cards
    concept_cards = [
        ("Target User", [
            "• Mahasiswa & pembelajar bahasa Inggris (EFL) usia 18–25 tahun.",
            "• Berada pada tingkat kemahiran intermediate (CEFR Level B1–B2).",
            "• Mengalami kecemasan berbicara (Foreign Language Speaking Anxiety / Xenoglossophobia) dan minim mitra wicara mandiri."
        ], ACCENT_BLUE),
        ("Learning Content", [
            "• Kurikulum terstruktur CEFR B1–B2 (18 modul skenario percakapan praktis).",
            "• Topik: Daily Conversation, Academic Life, Job Interview, dan Travel.",
            "• Pendekatan Microlearning: Sesi ringkas 3–5 menit (6–10 putaran dialog interaktif) dengan umpan balik langsung (corrective feedback)."
        ], PRIMARY_NAVY),
        ("Technology & Innovation", [
            "• Multimodal Generative AI: Whisper ASR + GPT-4o-mini + OpenAI TTS-1.",
            "• Knowledge-Grounded RAG: ChromaDB + BM25 Reciprocal Rank Fusion (RRF).",
            "• Interactive 2D Companion: Live2D Cubism WebGL dengan lip-sync berbasis amplitude audio wicara dan gamifikasi keterlibatan (XP, Streak, Badges)."
        ], TEAL),
    ]

    card_y = Inches(1.6)
    card_h = Inches(1.55)
    card_gap = Inches(0.2)
    card_w = Inches(6.8)

    for i, (title, bullets, col) in enumerate(concept_cards):
        cy = card_y + i * (card_h + card_gap)
        c = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.7), cy, card_w, card_h)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = CARD_BORDER
        c.line.width = Pt(1.2)

        # Title bar
        t_box = s3.shapes.add_textbox(Inches(5.9), cy + Inches(0.08), card_w - Inches(0.4), Inches(0.4))
        p = t_box.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = title
        r.font.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = col

        # Content bullets
        b_box = s3.shapes.add_textbox(Inches(5.9), cy + Inches(0.42), card_w - Inches(0.4), card_h - Inches(0.5))
        tf = b_box.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.space_after = Pt(2)
            r = p.add_run()
            r.text = b
            r.font.size = Pt(10)
            r.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 4: DESIGN - SYSTEM & INTERACTION SETUP
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background_decor(s4, title_text="Design: System Architecture & Layout")

    # Left Container: SYSTEM PIPELINE
    sys_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(6.8), Inches(5.3))
    sys_card.fill.solid()
    sys_card.fill.fore_color.rgb = CARD_BG
    sys_card.line.color.rgb = CARD_BORDER
    sys_card.line.width = Pt(1.5)

    hdr_sys = s4.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(6.4), Inches(0.4))
    p = hdr_sys.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "CORE AI & MULTIMEDIA SYSTEM PIPELINE"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    # Input Box
    in_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(2.1), Inches(6.2), Inches(0.7))
    in_box.fill.solid()
    in_box.fill.fore_color.rgb = RGBColor(239, 246, 255)
    in_box.line.color.rgb = ACCENT_BLUE
    p = in_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "INPUT: Web Audio API Voice Capture (16 kHz Mono WAV) / Text"
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = ACCENT_BLUE

    # Arrow Down
    arr1 = s4.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(4.0), Inches(2.85), Inches(0.2), Inches(0.2))
    arr1.fill.solid()
    arr1.fill.fore_color.rgb = ACCENT_BLUE
    arr1.line.fill.background()

    # Process Box
    proc_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(3.1), Inches(6.2), Inches(2.2))
    proc_box.fill.solid()
    proc_box.fill.fore_color.rgb = RGBColor(248, 250, 252)
    proc_box.line.color.rgb = PRIMARY_NAVY
    tf_p = proc_box.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    r = p.add_run()
    r.text = "PROCESSING PIPELINE (FastAPI Backend):"
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY_NAVY

    proc_items = [
        "1. Whisper ASR: Transkripsi audio wicara ke teks akurat.",
        "2. Hybrid RAG (ChromaDB + BM25 RRF): Ekstraksi silabus CEFR B1-B2.",
        "3. LLM Dialogue Manager (GPT-4o-mini via Bifrost): The One-Question Rule.",
        "4. Adaptive Feedback Engine: Deteksi eror grammar & kalkulasi WPM.",
        "5. OpenAI TTS-1 ('nova'): Sintesis audio respons tutor wicara alami."
    ]
    for item in proc_items:
        p = tf_p.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run()
        r.text = item
        r.font.size = Pt(9.5)
        r.font.color.rgb = TEXT_DARK

    # Arrow Down
    arr2 = s4.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(4.0), Inches(5.35), Inches(0.2), Inches(0.2))
    arr2.fill.solid()
    arr2.fill.fore_color.rgb = TEAL
    arr2.line.fill.background()

    # Output Box
    out_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(5.6), Inches(6.2), Inches(0.9))
    out_box.fill.solid()
    out_box.fill.fore_color.rgb = RGBColor(240, 253, 250)
    out_box.line.color.rgb = TEAL
    tf_o = out_box.text_frame
    tf_o.word_wrap = True
    p = tf_o.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "OUTPUT INTERACTIVE MULTIMEDIA"
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = TEAL
    p2 = tf_o.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Live2D Avatar Lip-Sync (ParamMouthOpenY) + Audio Voice + Kartu Koreksi Pedagogis"
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

    # Right Container: USER INTERACTION SETUP
    setup_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.5), Inches(4.5), Inches(5.3))
    setup_card.fill.solid()
    setup_card.fill.fore_color.rgb = CARD_BG
    setup_card.line.color.rgb = CARD_BORDER
    setup_card.line.width = Pt(1.5)

    hdr_setup = s4.shapes.add_textbox(Inches(8.2), Inches(1.6), Inches(4.1), Inches(0.4))
    p = hdr_setup.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "USER INTERACTION ENVIRONMENT"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    # Illustration text / breakdown
    setup_tb = s4.shapes.add_textbox(Inches(8.2), Inches(2.1), Inches(4.1), Inches(4.5))
    tf_s = setup_tb.text_frame
    tf_s.word_wrap = True

    specs = [
        ("Client Hardware:", "Laptop / PC dengan Headset & Mikrofon standar."),
        ("User Interface:", "Single Page Application (HTML5, Tailwind CSS, Live2D WebGL)."),
        ("Persona Effect:", "Karakter 2D MILO interaktif di layar mereduksi kecemasan wicara (affective filter) dibanding berbicara dengan native speaker asing."),
        ("Audio Synchronizer:", "Web Audio AnalyserNode menangkap gelombang amplitudo suara TTS untuk menggerakkan bibir model avatar secara real-time."),
        ("Network Protocol:", "FastAPI REST API & WebSocket asynchronous non-blocking.")
    ]
    for lbl, desc in specs:
        p = tf_s.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        r.text = lbl + " "
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = ACCENT_BLUE
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 5: DESIGN - USER FLOW & GAME LOOP
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background_decor(s5, title_text="Design: User Flow & Game Loop")

    # Left Side: User Flow Diagram
    flow_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(6.5), Inches(5.3))
    flow_box.fill.solid()
    flow_box.fill.fore_color.rgb = CARD_BG
    flow_box.line.color.rgb = CARD_BORDER
    flow_box.line.width = Pt(1.5)

    hdr_fl = s5.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(6.1), Inches(0.4))
    p = hdr_fl.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "USER FLOW DIAGRAM"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    flow_steps = [
        "1. Mulai: Registrasi / Login Akun Pengguna",
        "2. Diagnostic Placement Test (Klasifikasi CEFR B1 vs B2)",
        "3. Beranda Dashboard: Pilih Topik Skenario & Target Harian",
        "4. Briefing Sesi: Membaca Kosakata Kunci & Panduan Dialog",
        "5. Sesi Latihan Interaktif (Push-to-Talk ➔ ASR ➔ RAG+LLM ➔ TTS+Live2D)",
        "6. Stepper Check: 6–10 Putaran Percakapan Microlearning",
        "7. Summary Report: Tinjauan Eror Grammar, Fluency WPM, & Riwayat Skor",
        "8. Gamification Reward: Perolehan Poin XP, Streak Harian, & Lencana"
    ]

    tf_flow = s5.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(6.1), Inches(4.5)).text_frame
    tf_flow.word_wrap = True
    for i, step in enumerate(flow_steps):
        p = tf_flow.paragraphs[0] if i == 0 else tf_flow.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        r.text = step
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_DARK

    # Right Side: Gamification & Learning Loop
    loop_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.7), Inches(1.5), Inches(4.8), Inches(5.3))
    loop_box.fill.solid()
    loop_box.fill.fore_color.rgb = CARD_BG
    loop_box.line.color.rgb = CARD_BORDER
    loop_box.line.width = Pt(1.5)

    hdr_lp = s5.shapes.add_textbox(Inches(7.9), Inches(1.6), Inches(4.4), Inches(0.4))
    p = hdr_lp.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "CORE LEARNING & GAMIFICATION LOOP"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    loop_items = [
        ("DIAGNOSTIC / TOPIK", "Pilih topik microlearning sesuai level kemahiran B1 atau B2.", ACCENT_BLUE),
        ("PRACTICE WITH MILO", "Bicara langsung via suara, asisten merespons dengan dialog aktif.", PRIMARY_NAVY),
        ("ADAPTIVE FEEDBACK", "Koreksi tata bahasa seketika tanpa memutus alur percakapan.", TEAL),
        ("XP, STREAK & BADGES", "Penghargaan poin dan streak memicu motivasi latihan berkelanjutan.", AMBER),
    ]

    for k, (title, desc, col) in enumerate(loop_items):
        yk = Inches(2.2) + k * Inches(1.1)
        card_l = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), yk, Inches(4.2), Inches(0.85))
        card_l.fill.solid()
        card_l.fill.fore_color.rgb = RGBColor(248, 250, 252)
        card_l.line.color.rgb = col
        card_l.line.width = Pt(1.2)
        
        tf_l = card_l.text_frame
        tf_l.word_wrap = True
        p1 = tf_l.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = col

        p2 = tf_l.add_paragraph()
        r2 = p2.add_run()
        r2.text = desc
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 6: DESIGN - WIREFRAME & HIGH FIDELITY
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background_decor(s6, title_text="Design: Wireframe & High-Fidelity UI")

    # Wireframe Column
    wf_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    wf_box.fill.solid()
    wf_box.fill.fore_color.rgb = CARD_BG
    wf_box.line.color.rgb = CARD_BORDER
    wf_box.line.width = Pt(1.5)

    hdr_wf = s6.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(0.4))
    p = hdr_wf.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "WIREFRAME & STRUKTUR HALAMAN"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    wf_desc = [
        "1. Login / Register: Formulir autentikasi akun & token JWT.",
        "2. Diagnostic Test (setup-level.html): Pengujian wicara 4 domain untuk kalibrasi skor level B1 vs B2.",
        "3. Dashboard (dashboard.html): Kartu ringkasan kemahiran, penanda streak api harian, dan katalog modul pembelajaran.",
        "4. Practice Room (practice.html): Ruang latihan interaktif memuat kanvas WebGL Live2D, balon dialog, tombol Push-to-Talk, dan visual turn stepper.",
        "5. Summary Page (summary.html): Lembar evaluasi sesi, akurasi grammar, rincian feedback, dan klaim XP."
    ]
    tf_wf = s6.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.2), Inches(4.5)).text_frame
    tf_wf.word_wrap = True
    for i, w in enumerate(wf_desc):
        p = tf_wf.paragraphs[0] if i == 0 else tf_wf.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        r.text = w
        r.font.size = Pt(9.5)
        r.font.color.rgb = TEXT_DARK

    # High Fidelity Column
    hi_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    hi_box.fill.solid()
    hi_box.fill.fore_color.rgb = CARD_BG
    hi_box.line.color.rgb = CARD_BORDER
    hi_box.line.width = Pt(1.5)

    hdr_hi = s6.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(0.4))
    p = hdr_hi.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "HIGH-FIDELITY IMPLEMENTATION"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = ACCENT_BLUE

    hi_features = [
        ("Design System Tailwind:", "Antarmuka responsif dengan skema warna ramah, modern, dan bebas distraksi visual."),
        ("Live2D Avatar Integration:", "Model 2D MILO tampil hidup dengan kedipan mata, pandangan dinamis, dan gerakan idle alami."),
        ("Waveform Visualizer:", "Indikator visual gelombang suara real-time saat pengguna berbicara memberikan konfirmasi umpan balik audio."),
        ("Dynamic Feedback Drawer:", "Kartu umpan balik grammar adaptif yang dapat disembunyikan agar pembelajar tetap fokus pada kelancaran wicara."),
        ("Turn Counter Stepper:", "Komponen interaktif 'Turn 3 of 8' memberikan kepastian durasi microlearning.")
    ]
    tf_hi = s6.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.5)).text_frame
    tf_hi.word_wrap = True
    for lbl, desc in hi_features:
        p = tf_hi.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        r.text = lbl + " "
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = PRIMARY_NAVY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 7: MATERIAL COLLECTING
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background_decor(s7, title_text="Material Collecting")

    # Left: Visual & Knowledge Assets
    add_card(s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(3.6), "VISUAL & KNOWLEDGE ASSETS", [
        "• Model Karakter 2D (Live2D Cubism 4 SDK): Karakter MILO dengan tekstur ekspresi ramah, rigging mulut, kedipan mata, dan arah tatapan kepala.",
        "• Modul Pengetahuan CEFR (Obsidian Vault): 18 dokumen silabus terstruktur level B1–B2 (Cambridge Upper-Intermediate, Collins Speaking, IELTS).",
        "• Vektor Knowledge Base: Diindeks ke ChromaDB dengan embedding text-embedding-3-small (chunk 500 karakter).",
        "• Profil Suara Neural: OpenAI TTS-1 dengan profil suara 'nova' yang artikulatif, ekspresif, dan ramah bagi pembelajar."
    ], header_color=PRIMARY_NAVY)

    # Right: Moodboard & Design Palette
    add_card(s7, Inches(6.8), Inches(1.5), Inches(5.7), Inches(3.6), "DESIGN SYSTEM & MOODBOARD", [
        "• Primary Indigo (#4F46E5 & #1E293B): Menciptakan nuansa profesional, fokus, dan stabil dalam proses belajar.",
        "• Warm Amber (#F59E0B): Digunakan pada widget streak api, lencana, dan perolehan XP untuk memantik semangat kompetitif sehat.",
        "• Calm White (#F8FAFC): Mengurangi beban kognitif visual (cognitive load) selama latihan wicara berlangsung.",
        "• Tipografi Inter / Plus Jakarta Sans: Keterbacaan teks optimal pada berbagai ukuran resolusi layar."
    ], header_color=ACCENT_BLUE)

    # Bottom Callout / Pedagogical Theory
    callout = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.5))
    callout.fill.solid()
    callout.fill.fore_color.rgb = RGBColor(238, 242, 255)
    callout.line.color.rgb = ACCENT_BLUE
    callout.line.width = Pt(1.2)
    tf_c = callout.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    r = p.add_run()
    r.text = "LANDASAN PSIKOPEDAGOGIS: REDUKSI AFFECTIVE FILTER"
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = ACCENT_BLUE

    p2 = tf_c.add_paragraph()
    r2 = p2.add_run()
    r2.text = (
        "Berdasarkan Affective Filter Hypothesis (Krashen, 1982), kecemasan berbicara bahasa asing menghambat pemerolehan bahasa. "
        "Kombinasi persona 2D yang bersahabat, warna hangat, dan umpan balik tanpa penghakiman menciptakan lingkungan 'safe space' "
        "yang terbukti efektif menurunkan rasa takut salah (fear of negative evaluation) pada mahasiswa."
    )
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 8: ASSEMBLY - TECHNICAL INTEGRATION
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background_decor(s8, title_text="Assembly: Technical Pipeline Integration")

    pillars = [
        ("Whisper ASR Integration", [
            "• Web Audio capture 16 kHz mono dialirkan dari peramban.",
            "• Backend app/core/asr.py memproses berkas audio via Whisper API.",
            "• Menghasilkan teks transkripsi dengan akurasi tinggi terhadap aksen non-native.",
            "• Response time rata-rata di bawah 800 ms."
        ], ACCENT_BLUE),
        ("Hybrid RAG & LLM Orchestrator", [
            "• ChromaDB vector store + BM25 reciprocal rank fusion (k=60).",
            "• Prompt scaffolding membatasi kosa kata & struktur kalimat sesuai CEFR B1 vs B2.",
            "• The One-Question Rule memastikan tutor selalu mengembalikan giliran bicara ke siswa.",
            "• Terhubung via Bifrost AI Gateway (token budgeting & caching)."
        ], PRIMARY_NAVY),
        ("Live2D WebGL & TTS Lip-Sync", [
            "• OpenAI TTS-1 profil suara 'nova' menghasilkan audio MP3 responsif.",
            "• Web Audio API AnalyserNode mengekstrak amplitudo volume (RMS).",
            "• Memetakan level amplitudo ke parameter mulut ParamMouthOpenY.",
            "• Sinkronisasi bibir dan suara menghidupkan ilusi kehadiran sosial (social presence)."
        ], TEAL),
    ]

    card_w8 = Inches(3.64)
    for i, (title, bullets, col) in enumerate(pillars):
        x = Inches(0.8) + i * (card_w8 + Inches(0.4))
        add_card(s8, x, Inches(1.6), card_w8, Inches(5.1), title, bullets, header_color=col)

    # ==========================================
    # SLIDE 9: PROGRESS DOCUMENTATION
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background_decor(s9, title_text="Progress Documentation & System Audit")

    # Left: Audit Summary Table
    audit_card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.2))
    audit_card.fill.solid()
    audit_card.fill.fore_color.rgb = CARD_BG
    audit_card.line.color.rgb = CARD_BORDER
    audit_card.line.width = Pt(1.5)

    hdr_a = s9.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(7.1), Inches(0.4))
    p = hdr_a.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "REKAPITULASI PROGRES RIIL PENGERJAAN PA (TOTAL: 75.28%)"
    r.font.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = PRIMARY_NAVY

    # Table
    table_shape = s9.shapes.add_table(4, 5, Inches(1.0), Inches(2.1), Inches(7.1), Inches(2.2))
    table = table_shape.table
    table.columns[0].width = Inches(1.0) # RQ
    table.columns[1].width = Inches(2.5) # Fokus
    table.columns[2].width = Inches(0.8) # Bobot
    table.columns[3].width = Inches(0.8) # Progres
    table.columns[4].width = Inches(2.0) # Status

    headers = ["RQ", "Fokus Pengembangan", "Bobot", "Progres", "Status Evaluasi"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY_NAVY
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    data = [
        ("RQ-A", "Platform Web & Latihan Mandiri CEFR", "30%", "85.0%", "Selesai (Done)"),
        ("RQ-B", "Core AI Pipeline (ASR, RAG, LLM, TTS)", "40%", "86.0%", "Selesai (Done)"),
        ("RQ-C", "Live2D Avatar, Gamifikasi, Engagement", "30%", "51.25%", "In Progress (Finishing)"),
    ]

    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if i % 2 == 0 else RGBColor(255, 255, 255)
            p = cell.text_frame.paragraphs[0]
            if j in [0, 2, 3]:
                p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = val
            r.font.size = Pt(9)
            if j == 4:
                r.font.color.rgb = TEAL if "Selesai" in val else AMBER
                r.font.bold = True
            else:
                r.font.color.rgb = TEXT_DARK

    # Audit Notes below table
    tf_notes = s9.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(7.1), Inches(2.0)).text_frame
    tf_notes.word_wrap = True
    p = tf_notes.paragraphs[0]
    r = p.add_run()
    r.text = "Sorotan Pencapaian Sistem:"
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = ACCENT_BLUE

    notes = [
        "✔ Backend FastAPI, PostgreSQL, dan SQLAlchemy async beroperasi penuh.",
        "✔ Transkripsi wicara ASR Whisper & sintesis audio TTS terintegrasi lancar.",
        "✔ RAG 18 dokumen silabus CEFR B1-B2 terindeks dengan pencarian hibrida RRF.",
        "✔ Model Live2D berhasil ter-render WebGL; saat ini dalam tahap penghubungan audio analyzer lip-sync."
    ]
    for n in notes:
        p = tf_notes.add_paragraph()
        p.space_after = Pt(2)
        r = p.add_run()
        r.text = n
        r.font.size = Pt(9)
        r.font.color.rgb = TEXT_DARK

    # Right: Character / UI Snapshot
    right_card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.5), Inches(3.9), Inches(5.2))
    right_card.fill.solid()
    right_card.fill.fore_color.rgb = RGBColor(238, 242, 255)
    right_card.line.color.rgb = RGBColor(199, 210, 254)
    right_card.line.width = Pt(1.5)

    img_milo2 = "frontend/assets/milo_2.png"
    if os.path.exists(img_milo2):
        try:
            s9.shapes.add_picture(img_milo2, Inches(9.3), Inches(1.8), height=Inches(4.5))
        except Exception as e:
            print("Error adding milo_2 on slide 9:", e)

    # ==========================================
    # SLIDE 10: TESTING
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background_decor(s10, title_text="Testing & Evaluation Strategy")

    test_cards = [
        ("Black Box Testing", "Validasi Fungsionalitas Sistem & Ketahanan Pipeline", [
            "• Pengujian end-to-end seluruh API endpoint (/voice, /chat, /placement, /feedback).",
            "• Validasi keandalan perekaman Web Audio pada peramban Chrome & Firefox.",
            "• Pengujian mekanisme isolasi sesi latihan dan integritas basis data relasional.",
            "• Verifikasi penanganan timeout dan error handling saat kehilangan koneksi."
        ], ACCENT_BLUE),
        ("DeepEval Benchmark", "Evaluasi Kuantitatif Kualitas AI (LLM-as-a-Judge)", [
            "• Faithfulness (Skor 1.0 / 100% Pass): Kepatuhan respons terhadap silabus Obsidian tanpa halusinasi.",
            "• Answer Relevancy (Skor 1.0 / 100% Pass): Ketepatan respons terhadap input dan kebutuhan siswa.",
            "• CEFR Adaptation: Validasi kepatuhan tata bahasa dan kosakata terhadap level target B1 vs B2.",
            "• One Question Rule: Verifikasi konsistensi pertanyaan pemantik di akhir setiap respons."
        ], PRIMARY_NAVY),
        ("Usability (UEQ) & N-Gain", "Evaluasi Keterlibatan Belajar & Pengalaman Pengguna (N=32)", [
            "• User Experience Questionnaire (UEQ): Mengukur 6 skala (Daya Tarik, Kejelasan, Efisiensi, Ketepatan, Stimulasi, Kebaharuan).",
            "• Normalized Gain (N-Gain Hake): Mengukur peningkatan kemahiran dan penurunan kecemasan berbicara siswa melalui pre-test dan post-test.",
            "• Evaluasi Student Engagement 3 dimensi Phil Hiver (Behavioral, Emotional, Cognitive)."
        ], TEAL),
    ]

    card_y10 = Inches(1.5)
    card_h10 = Inches(1.6)
    card_gap10 = Inches(0.2)
    card_w10 = Inches(11.7)

    for i, (title, subtitle, bullets, col) in enumerate(test_cards):
        cy = card_y10 + i * (card_h10 + card_gap10)
        c = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cy, card_w10, card_h10)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_BG
        c.line.color.rgb = CARD_BORDER
        c.line.width = Pt(1.2)

        # Title
        tb = s10.shapes.add_textbox(Inches(1.0), cy + Inches(0.06), card_w10 - Inches(0.4), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = title + "  —  "
        r.font.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = col
        r2 = p.add_run()
        r2.text = subtitle
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MUTED

        # Content bullets
        tb_c = s10.shapes.add_textbox(Inches(1.0), cy + Inches(0.38), card_w10 - Inches(0.4), card_h10 - Inches(0.42))
        tf = tb_c.text_frame
        tf.word_wrap = True
        for j, b in enumerate(bullets):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.space_after = Pt(1.5)
            r = p.add_run()
            r.text = b
            r.font.size = Pt(9.5)
            r.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 11: CONCLUSION & FUTURE PLAN
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_background_decor(s11, title_text="Conclusion & Future Plan")

    # Project Goal Card
    goal_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.2))
    goal_card.fill.solid()
    goal_card.fill.fore_color.rgb = CARD_BG
    goal_card.line.color.rgb = ACCENT_BLUE
    goal_card.line.width = Pt(1.5)

    tb_g = s11.shapes.add_textbox(Inches(1.1), Inches(1.65), Inches(11.1), Inches(1.9))
    tfg = tb_g.text_frame
    tfg.word_wrap = True
    p = tfg.paragraphs[0]
    r = p.add_run()
    r.text = "🎯 PROJECT GOAL (TUJUAN PENELITIAN PROYEK AKHIR)"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = ACCENT_BLUE

    p2 = tfg.add_paragraph()
    p2.space_before = Pt(6)
    r2 = p2.add_run()
    r2.text = (
        "Mengembangkan platform pembelajaran mandiri interaktif berbasis asisten virtual dua dimensi (2D) "
        "yang mengintegrasikan multimodal generative AI (Whisper ASR, Hybrid RAG ChromaDB, GPT-4o-mini, dan OpenAI TTS) "
        "guna meningkatkan keterlibatan belajar (student engagement) serta mereduksi kecemasan berbicara bahasa Inggris "
        "(speaking anxiety) pada pembelajar intermediate level CEFR B1–B2."
    )
    r2.font.size = Pt(11)
    r2.font.color.rgb = TEXT_DARK

    # Future Plan Card
    plan_card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.0), Inches(11.7), Inches(2.8))
    plan_card.fill.solid()
    plan_card.fill.fore_color.rgb = CARD_BG
    plan_card.line.color.rgb = TEAL
    plan_card.line.width = Pt(1.5)

    tb_p = s11.shapes.add_textbox(Inches(1.1), Inches(4.15), Inches(11.1), Inches(2.5))
    tfp = tb_p.text_frame
    tfp.word_wrap = True
    p = tfp.paragraphs[0]
    r = p.add_run()
    r.text = "⏱ FUTURE PLAN & ROADMAP PENYELESAIAN (TARGET 100%)"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = TEAL

    plans = [
        ("1. Real Audio Lip-Sync Live2D (Prioritas 1):", "Menyambungkan Web Audio API AnalyserNode ke parameter mulut ParamMouthOpenY untuk akurasi sinkronisasi ucapan audio TTS nyata."),
        ("2. Polesan Visual Antarmuka Gamifikasi (Prioritas 1):", "Mempercantik widget streak api, dynamic XP progress bar, modal perayaan lencana, dan turn stepper di peramban."),
        ("3. Pengambilan Data Responden N=32 (Prioritas 2):", "Melaksanakan uji pre-test dan post-test, menyebarkan kuesioner UEQ & keterlibatan siswa, serta menghitung skor N-Gain Hake."),
        ("4. Finalisasi Laporan Akhir & Ujian Sidang:", "Melengkapi data Bab 4 & Bab 5 pada Buku Progres dan Buku Laporan Akhir sesuai standar 5 Bab PENS TRM.")
    ]
    for lbl, desc in plans:
        p = tfp.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        r.text = lbl + " "
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = PRIMARY_NAVY
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 12: THANK YOU
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_background_decor(s12, show_page_arrow=False)

    # Big Diagonal Header Banner
    banner = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.12), Inches(13.333), Inches(2.2))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(224, 231, 255)
    banner.line.fill.background()

    # Thank you box
    tb_ty = s12.shapes.add_textbox(Inches(1.0), Inches(2.8), Inches(11.333), Inches(1.8))
    tf_ty = tb_ty.text_frame
    p = tf_ty.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Thank You!"
    r.font.bold = True
    r.font.size = Pt(48)
    r.font.color.rgb = PRIMARY_NAVY

    p2 = tf_ty.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = "Terima Kasih Atas Perhatian Bapak / Ibu Dosen Penguji & Pembimbing"
    r2.font.size = Pt(16)
    r2.font.color.rgb = ACCENT_BLUE

    # Closing Card with author details
    ty_card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.666), Inches(4.7), Inches(6.0), Inches(2.0))
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = CARD_BG
    ty_card.line.color.rgb = CARD_BORDER
    ty_card.line.width = Pt(1)

    tf_c = ty_card.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Siti Maulana Shofiyah"
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = PRIMARY_NAVY

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "NRP. 5323600043"
    r.font.size = Pt(11)
    r.font.color.rgb = TEXT_MUTED

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Program Studi Sarjana Terapan Teknologi Rekayasa Multimedia (TRM)"
    r.font.size = Pt(10.5)
    r.font.color.rgb = PRIMARY_NAVY

    p = tf_c.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Jurusan Teknologi Multimedia Kreatif — Politeknik Elektronika Negeri Surabaya"
    r.font.size = Pt(9.5)
    r.font.color.rgb = TEXT_MUTED

    # Save presentation
    prs.save(output_path)
    print(f"Presentation generated successfully at: {output_path}")

if __name__ == "__main__":
    create_deck()
