import os

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 820" width="100%" height="100%" style="background-color: #FFFFFF; font-family: 'Segoe UI', 'Inter', Arial, sans-serif;">
  <defs>
    <!-- Subtle Drop Shadow -->
    <filter id="cardShadow" x="-4%" y="-4%" width="108%" height="112%" filterUnits="userSpaceOnUse">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3.5"/>
      <feOffset dx="0" dy="2.5"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.07"/></feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <!-- Arrow Markers -->
    <marker id="arrSlate" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#475569"/>
    </marker>
    <marker id="arrIndigo" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#4F46E5"/>
    </marker>
    <marker id="arrBlue" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#2563EB"/>
    </marker>
    <marker id="arrPurple" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#9333EA"/>
    </marker>
    <marker id="arrTeal" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#0D9488"/>
    </marker>
    <marker id="arrPink" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="#DB2777"/>
    </marker>
  </defs>

  <!-- ==================== HEADER ==================== -->
  <text x="620" y="36" text-anchor="middle" font-size="19" font-weight="700" fill="#0F172A" letter-spacing="0.3">
    ARSITEKTUR PIPELINE ADAPTIVE HYBRID RAG (INGESTI &amp; PENELUSURAN)
  </text>
  <text x="620" y="58" text-anchor="middle" font-size="12.5" fill="#64748B">
    Sistem AI-MILO: Integrasi Dense Semantic Search (ChromaDB) dan Sparse Lexical Search (BM25) dengan Reciprocal Rank Fusion
  </text>

  <!-- ==================== ZONE 1: OFFLINE INGESTION (LEFT) ==================== -->
  <rect x="24" y="82" width="356" height="470" rx="12" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="6,4"/>
  <rect x="40" y="96" width="324" height="30" rx="6" fill="#4F46E5"/>
  <text x="202" y="116" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF" letter-spacing="0.4">
    1. TAHAP INGESTI DATA (OFFLINE)
  </text>

  <!-- 1.1 Knowledge Base Docs -->
  <g filter="url(#cardShadow)">
    <rect x="44" y="144" width="316" height="68" rx="8" fill="#EEF2FF" stroke="#4F46E5" stroke-width="1.6"/>
    <circle cx="64" cy="164" r="10" fill="#4F46E5"/>
    <text x="64" y="168" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">1</text>
    <text x="210" y="170" text-anchor="middle" font-size="13" font-weight="700" fill="#1E1B4B">Dokumen Silabus CEFR B1–B2</text>
    <text x="202" y="191" text-anchor="middle" font-size="11" fill="#4338CA">Korpus Markdown &amp; 18 Modul Microlearning</text>
  </g>

  <!-- Arrow 1.1 -> 1.2 -->
  <line x1="202" y1="212" x2="202" y2="238" stroke="#4F46E5" stroke-width="2" marker-end="url(#arrIndigo)"/>

  <!-- 1.2 Text Splitter -->
  <g filter="url(#cardShadow)">
    <rect x="44" y="242" width="316" height="68" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="1.6"/>
    <circle cx="64" cy="262" r="10" fill="#16A34A"/>
    <text x="64" y="266" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">2</text>
    <text x="210" y="268" text-anchor="middle" font-size="12.5" font-weight="700" fill="#14532D">RecursiveCharacterTextSplitter</text>
    <text x="202" y="289" text-anchor="middle" font-size="11" fill="#15803D">Chunk Size: 500 Karakter | Overlap: 50 Karakter</text>
  </g>

  <!-- Split Arrows from 1.2 to Dense (top-right) & Sparse (bottom-right) -->
  <!-- Wait: Let's stack Dense Embed (y=342) and Sparse Token (y=446) vertically on the left, OR side by side? -->
  <!-- Stacking them vertically aligns Dense Embed directly with ChromaDB (top) and Sparse Token with BM25 (bottom)! ZERO CROSSING! -->
  <path d="M 110 310 L 110 378 L 135 378" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arrBlue)"/>
  <path d="M 82 310 L 82 482 L 135 482" fill="none" stroke="#9333EA" stroke-width="2" marker-end="url(#arrPurple)"/>

  <!-- 1.3 Dense Embedding Box (Aligned with ChromaDB) -->
  <g filter="url(#cardShadow)">
    <rect x="140" y="338" width="220" height="80" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.6"/>
    <text x="250" y="362" text-anchor="middle" font-size="12" font-weight="700" fill="#1E3A8A">Jalur 1: Dense Embedding</text>
    <text x="250" y="382" text-anchor="middle" font-size="11" fill="#1D4ED8">OpenAI text-embedding-3-small</text>
    <text x="250" y="400" text-anchor="middle" font-size="10.5" font-weight="600" fill="#3B82F6">Vektor 1536 Dimensi</text>
  </g>

  <!-- 1.4 Sparse Tokenizer Box (Aligned with BM25) -->
  <g filter="url(#cardShadow)">
    <rect x="140" y="442" width="220" height="80" rx="8" fill="#FAF5FF" stroke="#9333EA" stroke-width="1.6"/>
    <text x="250" y="466" text-anchor="middle" font-size="12" font-weight="700" fill="#581C87">Jalur 2: Sparse Tokenizer</text>
    <text x="250" y="486" text-anchor="middle" font-size="11" fill="#7E22CE">BM25 Lexical Parser</text>
    <text x="250" y="504" text-anchor="middle" font-size="10.5" font-weight="600" fill="#9333EA">Tokenisasi Kata Kunci &amp; TF-IDF</text>
  </g>


  <!-- ==================== ZONE 2: HYBRID STORAGE (CENTER) ==================== -->
  <rect x="404" y="295" width="224" height="257" rx="12" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.5" stroke-dasharray="6,4"/>
  <rect x="418" y="308" width="196" height="24" rx="5" fill="#D97706"/>
  <text x="516" y="324" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF" letter-spacing="0.3">
    BASIS PENGETAHUAN HIBRIDA
  </text>

  <!-- Straight Horizontal Arrows: Zone 1 -> Zone 2 -->
  <line x1="360" y1="378" x2="416" y2="378" stroke="#2563EB" stroke-width="2" marker-end="url(#arrBlue)"/>
  <line x1="360" y1="482" x2="416" y2="482" stroke="#9333EA" stroke-width="2" marker-end="url(#arrPurple)"/>

  <!-- 2.1 ChromaDB Cylinder Card -->
  <g filter="url(#cardShadow)">
    <rect x="420" y="342" width="192" height="74" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="1.8"/>
    <path d="M 436 362 C 436 356, 460 356, 460 362 C 460 368, 436 368, 436 362 Z M 436 362 L 436 382 C 436 388, 460 388, 460 382 L 460 362" fill="#FDE68A" stroke="#B45309" stroke-width="1.4"/>
    <text x="532" y="366" text-anchor="middle" font-size="12.5" font-weight="700" fill="#78350F">ChromaDB</text>
    <text x="532" y="384" text-anchor="middle" font-size="10.5" fill="#92400E">HNSW Vector Index</text>
    <text x="532" y="401" text-anchor="middle" font-size="10" font-weight="600" fill="#B45309">Cosine Distance Metric</text>
  </g>

  <!-- 2.2 BM25 Index Cylinder Card -->
  <g filter="url(#cardShadow)">
    <rect x="420" y="446" width="192" height="74" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="1.8"/>
    <path d="M 436 466 C 436 460, 460 460, 460 466 C 460 472, 436 472, 436 466 Z M 436 466 L 436 486 C 436 492, 460 492, 460 486 L 460 466" fill="#FDE68A" stroke="#B45309" stroke-width="1.4"/>
    <text x="532" y="470" text-anchor="middle" font-size="12.5" font-weight="700" fill="#78350F">BM25 Index</text>
    <text x="532" y="488" text-anchor="middle" font-size="10.5" fill="#92400E">In-Memory Inverted Index</text>
    <text x="532" y="505" text-anchor="middle" font-size="10" font-weight="600" fill="#B45309">Term Freq &amp; Doc Norm</text>
  </g>

  <!-- Info Box under Zone 1 & 2 -->
  <g filter="url(#cardShadow)">
    <rect x="24" y="574" width="604" height="218" rx="10" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5"/>
    <text x="44" y="602" font-size="12.5" font-weight="700" fill="#1E293B">RINGKASAN SPESIFIKASI TEKNIS HYBRID RAG</text>
    <line x1="44" y1="612" x2="608" y2="612" stroke="#E2E8F0" stroke-width="1.2"/>
    
    <text x="48" y="636" font-size="11.5" font-weight="700" fill="#4F46E5">• Segmentasi Dokumen (Chunking):</text>
    <text x="260" y="636" font-size="11.5" fill="#334155">500 karakter per potongan, overlap 50 karakter.</text>

    <text x="48" y="662" font-size="11.5" font-weight="700" fill="#2563EB">• Penelusuran Semantik (Dense):</text>
    <text x="260" y="662" font-size="11.5" fill="#334155">Cosine Similarity &gt;= 0.70 pada ruang 1536 dimensi.</text>

    <text x="48" y="688" font-size="11.5" font-weight="700" fill="#9333EA">• Penelusuran Leksikal (Sparse):</text>
    <text x="260" y="688" font-size="11.5" fill="#334155">Algoritma BM25 untuk kecocokan istilah grammar spesifik.</text>

    <text x="48" y="714" font-size="11.5" font-weight="700" fill="#DB2777">• Penggabungan Peringkat (RRF):</text>
    <text x="260" y="714" font-size="11.5" fill="#334155">Formula RRF(d) = Σ 1 / (60 + r_m(d)), memilih Top-3 (k = 3).</text>

    <text x="48" y="740" font-size="11.5" font-weight="700" fill="#0D9488">• Dukungan Offline Fallback:</text>
    <text x="260" y="740" font-size="11.5" fill="#334155">18 modul microlearning direplikasi di curriculum-data.js.</text>

    <text x="48" y="766" font-size="11.5" font-weight="700" fill="#7C3AED">• Orkestrasi Gateway:</text>
    <text x="260" y="766" font-size="11.5" fill="#334155">Bifrost AI Gateway (Rate Limit 60 req/m, Cache &gt;= 0.95).</text>
  </g>


  <!-- ==================== ZONE 3: ONLINE RETRIEVAL & GENERATION (RIGHT) ==================== -->
  <rect x="652" y="82" width="564" height="710" rx="12" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" stroke-dasharray="6,4"/>
  <rect x="668" y="96" width="532" height="30" rx="6" fill="#0D9488"/>
  <text x="934" y="116" text-anchor="middle" font-size="12" font-weight="700" fill="#FFFFFF" letter-spacing="0.4">
    2. TAHAP PENELUSURAN CERDAS &amp; PENALARAN (ONLINE)
  </text>

  <!-- 3.1 User Query -->
  <g filter="url(#cardShadow)">
    <rect x="704" y="144" width="460" height="68" rx="8" fill="#F0FDFA" stroke="#0D9488" stroke-width="1.6"/>
    <circle cx="724" cy="164" r="10" fill="#0D9488"/>
    <text x="724" y="168" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">3</text>
    <text x="934" y="170" text-anchor="middle" font-size="13" font-weight="700" fill="#134E4A">Masukan Wicara Pengguna (Kueri)</text>
    <text x="934" y="191" text-anchor="middle" font-size="11" fill="#0F766E">Transkripsi Teks Real-time via OpenAI Whisper ASR</text>
  </g>

  <!-- Parallel Query Arrows from 3.1 to Dense Search (y=338) & Sparse Search (y=442) -->
  <!-- Wait: Let's place Dense Search and Sparse Search side-by-side or stacked? -->
  <!-- If Dense Search is Top (y=342) and Sparse Search is Bottom (y=446), wait: User Query is at y=144! -->
  <!-- Even better: Place Dense Search at y=240 (left of right zone) and Sparse Search at y=240 (right of right zone)? No, then lines from ChromaDB/BM25 would cross! -->
  <!-- So let's keep Dense Search at y=342 and Sparse Search at y=446, OR route User Query down the right side! -->
  <!-- Look how clean routing User Query down the RIGHT edge is: -->
  <path d="M 1164 178 L 1188 178 L 1188 378 L 1106 378" fill="none" stroke="#0D9488" stroke-width="2" marker-end="url(#arrTeal)"/>
  <path d="M 1188 378 L 1188 482 L 1106 482" fill="none" stroke="#0D9488" stroke-width="2" marker-end="url(#arrTeal)"/>

  <!-- Put a Query Embedder / Keyword Extractor box right under User Query at y=236! -->
  <g filter="url(#cardShadow)">
    <rect x="704" y="234" width="460" height="62" rx="8" fill="#FFFFFF" stroke="#0D9488" stroke-width="1.4"/>
    <text x="934" y="259" text-anchor="middle" font-size="12" font-weight="700" fill="#134E4A">Ekstraksi Fitur Kueri Ganda (Dual Query Representation)</text>
    <text x="934" y="279" text-anchor="middle" font-size="11" fill="#0F766E">Vektor Kueri (1536 Dim) &amp; Token Kata Kunci Leksikal</text>
  </g>
  <line x1="934" y1="212" x2="934" y2="230" stroke="#0D9488" stroke-width="2" marker-end="url(#arrTeal)"/>
  <!-- Route from Dual Query box (y=265) along the right rail (x=1188) to Dense Search and Sparse Search -->
  <path d="M 1164 265 L 1188 265 L 1188 378 L 1106 378" fill="none" stroke="#0D9488" stroke-width="2" marker-end="url(#arrTeal)"/>

  <!-- Straight Dashed Arrows from Zone 2 (Storage) -> Zone 3 (Search)! ZERO CROSSING! -->
  <line x1="612" y1="378" x2="684" y2="378" stroke="#2563EB" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrBlue)"/>
  <line x1="612" y1="482" x2="684" y2="482" stroke="#9333EA" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrPurple)"/>

  <!-- 3.2 Dense Semantic Search (Aligned horizontally with ChromaDB!) -->
  <g filter="url(#cardShadow)">
    <rect x="690" y="342" width="410" height="74" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.6"/>
    <text x="895" y="366" text-anchor="middle" font-size="12.5" font-weight="700" fill="#1E3A8A">Dense Semantic Search (ChromaDB)</text>
    <text x="895" y="385" text-anchor="middle" font-size="11" fill="#1D4ED8">Hitung Cosine Similarity(q, d) &gt;= 0.70</text>
    <text x="895" y="403" text-anchor="middle" font-size="10.5" font-weight="600" fill="#3B82F6">Menghasilkan Peringkat Semantik: r_dense(d)</text>
  </g>

  <!-- 3.3 Sparse Lexical Search (Aligned horizontally with BM25 Index!) -->
  <g filter="url(#cardShadow)">
    <rect x="690" y="446" width="410" height="74" rx="8" fill="#FAF5FF" stroke="#9333EA" stroke-width="1.6"/>
    <text x="895" y="470" text-anchor="middle" font-size="12.5" font-weight="700" fill="#581C87">Sparse Lexical Search (BM25)</text>
    <text x="895" y="489" text-anchor="middle" font-size="11" fill="#7E22CE">Pencocokan Kata Kunci &amp; Istilah Tata Bahasa</text>
    <text x="895" y="507" text-anchor="middle" font-size="10.5" font-weight="600" fill="#9333EA">Menghasilkan Peringkat Leksikal: r_sparse(d)</text>
  </g>

  <!-- Merge Arrows from Search Boxes (left rail x=670) -> RRF Box! -->
  <path d="M 690 395 L 672 395 L 672 568 L 700 568" fill="none" stroke="#2563EB" stroke-width="1.8" marker-end="url(#arrBlue)"/>
  <path d="M 690 498 L 672 498 L 672 568" fill="none" stroke="#9333EA" stroke-width="1.8"/>

  <!-- 3.4 Reciprocal Rank Fusion (RRF) -->
  <g filter="url(#cardShadow)">
    <rect x="704" y="538" width="460" height="66" rx="8" fill="#FDF2F8" stroke="#DB2777" stroke-width="1.8"/>
    <circle cx="724" cy="558" r="10" fill="#DB2777"/>
    <text x="724" y="562" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">4</text>
    <text x="934" y="561" text-anchor="middle" font-size="12.5" font-weight="700" fill="#831843">Reciprocal Rank Fusion (RRF) &amp; Top-3 Filter</text>
    <text x="934" y="581" text-anchor="middle" font-size="11" font-weight="600" fill="#BE185D">RRF(d) = Σ 1 / (60 + r_m(d))  →  Ambil Top-3 (k = 3)</text>
  </g>

  <!-- Arrow 3.4 -> 3.5 -->
  <line x1="934" y1="604" x2="934" y2="626" stroke="#DB2777" stroke-width="2" marker-end="url(#arrPink)"/>

  <!-- 3.5 Context Prompt Injection -->
  <g filter="url(#cardShadow)">
    <rect x="704" y="630" width="460" height="58" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="1.6"/>
    <circle cx="724" cy="650" r="10" fill="#D97706"/>
    <text x="724" y="654" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">5</text>
    <text x="934" y="653" text-anchor="middle" font-size="12" font-weight="700" fill="#78350F">Penyusunan Context Prompt Adaptif</text>
    <text x="934" y="672" text-anchor="middle" font-size="10.5" fill="#B45309">Top-3 Konteks Silabus + Riwayat Dialog + Aturan CEFR B1/B2</text>
  </g>

  <!-- Arrow 3.5 -> 3.6 -->
  <line x1="934" y1="688" x2="934" y2="708" stroke="#D97706" stroke-width="2" marker-end="url(#arrSlate)"/>

  <!-- 3.6 GPT-4o-mini LLM -->
  <g filter="url(#cardShadow)">
    <rect x="704" y="712" width="460" height="66" rx="8" fill="#F5F3FF" stroke="#7C3AED" stroke-width="2"/>
    <circle cx="724" cy="732" r="10" fill="#7C3AED"/>
    <text x="724" y="736" text-anchor="middle" font-size="10.5" font-weight="700" fill="#FFFFFF">6</text>
    <text x="934" y="736" text-anchor="middle" font-size="13" font-weight="700" fill="#4C1D95">GPT-4o-mini (via AI Gateway Bifrost)</text>
    <text x="934" y="757" text-anchor="middle" font-size="10.5" font-weight="600" fill="#6D28D9">Respons Tutor (One-Question Rule) + Koreksi Grammar (JSON)</text>
  </g>

</svg>
'''

with open("buku/Gambar_3_5_Pipeline_Hybrid_RAG.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("Upgraded 3-zone non-crossing SVG created at buku/Gambar_3_5_Pipeline_Hybrid_RAG.svg")
