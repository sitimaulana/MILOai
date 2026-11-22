"""
MILO AI Backend - Word Document (.docx) Generator
Generates a fully formatted Microsoft Word (.docx) manuscript for the TRM PENS Final Project Progress Book
directly from `buku/BUKU_PROGRES_PA_AI_MILO.md` adhering strictly to PENS TRM formatting rules.
"""

import os
import re
import zipfile
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MD_PATH = BASE_DIR / "buku" / "BUKU_PROGRES_PA_AI_MILO.md"
DOCX_PATH = BASE_DIR / "buku" / "BUKU_PROGRES_PA_AI_MILO.docx"

# XML Namespaces
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def escape_xml(text: str) -> str:
    """Escapes special characters for XML."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

def create_content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>"""

def create_root_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

def create_document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>"""

def create_settings_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:defaultTabStop w:val="708"/>
  <w:compat>
    <w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>
  </w:compat>
</w:settings>"""

def create_styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
        <w:lang w:val="id-ID"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="360" w:lineRule="auto" w:before="0" w:after="120"/>
        <w:jc w:val="both"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>

  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
      <w:color w:val="000000"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="180" w:after="80" w:line="360" w:lineRule="auto"/>
      <w:jc w:val="left"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:color w:val="000000"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="120" w:after="60" w:line="360" w:lineRule="auto"/>
      <w:jc w:val="left"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:i/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
      <w:color w:val="000000"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Caption">
    <w:name w:val="caption"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="80" w:after="120" w:line="240" w:lineRule="auto"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:rPr>
      <w:b/>
      <w:sz w:val="20"/>
      <w:szCs w:val="20"/>
    </w:rPr>
  </w:style>

  <w:style w:type="table" w:default="1" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:qFormat/>
    <w:tblPr>
      <w:tblBorders>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
      </w:tblBorders>
    </w:tblPr>
  </w:style>
</w:styles>"""

def build_paragraph(text: str, style: str = "Normal", bold: bool = False, italic: bool = False, 
                    align: str = "both", indent: bool = False, highlight: str = None, 
                    page_break_before: bool = False, center: bool = False) -> str:
    """Constructs a WordProcessingML <w:p> element."""
    p_props = []
    if style != "Normal":
        p_props.append(f'<w:pStyle w:val="{style}"/>')
    if page_break_before:
        p_props.append('<w:pageBreakBefore/>')
    if center or align == "center":
        p_props.append('<w:jc w:val="center"/>')
    elif align != "both":
        p_props.append(f'<w:jc w:val="{align}"/>')
    if indent:
        p_props.append('<w:ind w:firstLine="567"/>')  # 1 cm = 567 dxa
    
    p_pr = f"<w:pPr>{''.join(p_props)}</w:pPr>" if p_props else ""

    # Parse inline bold, italic, code spans
    runs_xml = []
    # If the paragraph is marked as a student callout / placeholder
    is_callout = text.startswith("[PANDUAN") or text.startswith("[ISI") or text.startswith("[TEMPELKAN") or "CATATAN UNTUK MAHASISWA" in text
    
    if is_callout:
        p_pr = '<w:pPr><w:pBdr><w:top w:val="single" w:sz="8" w:space="4" w:color="E67E22"/><w:left w:val="single" w:sz="24" w:space="8" w:color="E67E22"/><w:bottom w:val="single" w:sz="8" w:space="4" w:color="E67E22"/><w:right w:val="single" w:sz="8" w:space="4" w:color="E67E22"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="FFF3CD"/><w:spacing w:before="120" w:after="120" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
        run_pr = '<w:rPr><w:b/><w:i/><w:color w:val="856404"/></w:rPr>'
        escaped_t = escape_xml(text)
        runs_xml.append(f'<w:r>{run_pr}<w:t xml:space="preserve">{escaped_t}</w:t></w:r>')
        return f"<w:p>{p_pr}{''.join(runs_xml)}</w:p>"

    # Regular paragraph parsing: handle bold **text** and italic *text* and `code`
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for tok in tokens:
        if not tok:
            continue
        tok_b = bold
        tok_i = italic
        tok_code = False
        content = tok

        if tok.startswith("**") and tok.endswith("**") and len(tok) >= 4:
            tok_b = True
            content = tok[2:-2]
        elif tok.startswith("*") and tok.endswith("*") and len(tok) >= 2:
            tok_i = True
            content = tok[1:-1]
        elif tok.startswith("`") and tok.endswith("`") and len(tok) >= 2:
            tok_code = True
            content = tok[1:-1]

        r_pr_parts = []
        if tok_b:
            r_pr_parts.append("<w:b/>")
        if tok_i:
            r_pr_parts.append("<w:i/>")
        if tok_code:
            r_pr_parts.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
            r_pr_parts.append('<w:color w:val="C7254E"/>')
            r_pr_parts.append('<w:shd w:val="clear" w:color="auto" w:fill="F9F2F4"/>')
        if highlight:
            r_pr_parts.append(f'<w:highlight w:val="{highlight}"/>')

        r_pr = f"<w:rPr>{''.join(r_pr_parts)}</w:rPr>" if r_pr_parts else ""
        escaped_content = escape_xml(content)
        runs_xml.append(f'<w:r>{r_pr}<w:t xml:space="preserve">{escaped_content}</w:t></w:r>')

    return f"<w:p>{p_pr}{''.join(runs_xml)}</w:p>"

def build_table(table_rows: list) -> str:
    """Builds a WordProcessingML <w:tbl> element with clean borders and padded cells."""
    if not table_rows:
        return ""
    
    tbl_xml = [
        '<w:tbl>',
        '<w:tblPr>',
        '<w:tblStyle w:val="TableGrid"/>',
        '<w:tblW w:w="0" w:type="auto"/>',
        '<w:tblBorders>',
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>',
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>',
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>',
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>',
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>',
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>',
        '</w:tblBorders>',
        '<w:tblCellMar><w:top w:w="120" w:type="dxa"/><w:left w:w="160" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:right w:w="160" w:type="dxa"/></w:tblCellMar>',
        '<w:jc w:val="center"/>',
        '</w:tblPr>'
    ]

    for row_idx, row in enumerate(table_rows):
        is_header = (row_idx == 0)
        tbl_xml.append('<w:tr>')
        tr_pr = []
        if is_header:
            tr_pr.append('<w:tblHeader/>')
        tbl_xml.append(f"<w:trPr>{''.join(tr_pr)}</w:trPr>")

        for col in row:
            col_text = col.strip()
            tbl_xml.append('<w:tc>')
            tc_pr = []
            if is_header:
                tc_pr.append('<w:shd w:val="clear" w:color="auto" w:fill="E8EEF5"/>')
            tbl_xml.append(f"<w:tcPr>{''.join(tc_pr)}</w:tcPr>")
            
            p_xml = build_paragraph(
                col_text, 
                bold=is_header, 
                align="center" if is_header else "left", 
                indent=False
            )
            tbl_xml.append(p_xml)
            tbl_xml.append('</w:tc>')
        tbl_xml.append('</w:tr>')

    tbl_xml.append('</w:tbl>')
    return "".join(tbl_xml)

def convert_markdown_to_docx_body(md_content: str) -> str:
    """Parses markdown text and constructs the OpenXML <w:body> content."""
    lines = md_content.splitlines()
    body_xml = []
    
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "\n".join(code_lines)
                for c_line in code_lines:
                    body_xml.append(build_paragraph(c_line, bold=False, align="left", indent=False))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle Tables
        if "|" in line and (line.startswith("|") or line.endswith("|")):
            # Check if this is a separator row like |:---|---:|
            if re.match(r'^\|?\s*:?-+:?\s*(\|?\s*:?-+:?\s*)+\|?$', stripped):
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if cells:
                in_table = True
                table_rows.append(cells)
                continue
        else:
            if in_table:
                body_xml.append(build_table(table_rows))
                in_table = False
                table_rows = []

        # Blank line
        if not stripped:
            continue

        # Horizontal Rule (Page Break representation)
        if stripped in ["---", "***", "___"]:
            body_xml.append('<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr></w:p>')
            continue

        # Headings
        if stripped.startswith("# "):
            title_text = stripped[2:].strip()
            # Major chapters start on new page
            is_chapter = title_text.startswith("BAB ") or title_text in ["BUKU PROGRES PROYEK AKHIR", "ABSTRAK", "ABSTRACT", "KATA PENGANTAR", "DAFTAR ISI", "DAFTAR GAMBAR", "DAFTAR TABEL", "DAFTAR PUSTAKA", "LAMPIRAN"]
            body_xml.append(build_paragraph(title_text, style="Heading1", bold=True, center=True, page_break_before=is_chapter))
            continue
        elif stripped.startswith("## "):
            h2_text = stripped[3:].strip()
            is_major = h2_text in ["ABSTRAK", "ABSTRACT", "KATA PENGANTAR", "DAFTAR ISI", "DAFTAR GAMBAR", "DAFTAR TABEL", "DAFTAR PUSTAKA", "LAMPIRAN"] or h2_text.startswith("BAB ")
            body_xml.append(build_paragraph(h2_text, style="Heading1" if is_major else "Heading2", bold=True, center=is_major, page_break_before=is_major))
            continue
        elif stripped.startswith("### "):
            body_xml.append(build_paragraph(stripped[4:].strip(), style="Heading3", bold=True, italic=True, align="left"))
            continue

        # Figure / Table Captions
        if stripped.startswith("*Gambar ") or stripped.startswith("Gambar ") or stripped.startswith("**Gambar "):
            clean_cap = re.sub(r'[*_]', '', stripped)
            body_xml.append(build_paragraph(clean_cap, style="Caption", bold=True, center=True))
            # Append placeholder for actual image insert
            body_xml.append(build_paragraph(f"[TEMPELKAN SCREENSHOT / ILUSTRASI: {clean_cap}]", center=True))
            continue
        elif stripped.startswith("Tabel ") or stripped.startswith("**Tabel "):
            clean_tbl = re.sub(r'[*_]', '', stripped)
            body_xml.append(build_paragraph(clean_tbl, style="Caption", bold=True, center=True))
            continue

        # Mathematical equations ($$...$$)
        if stripped.startswith("$$") and stripped.endswith("$$"):
            eq_text = stripped[2:-2].strip()
            body_xml.append(build_paragraph(eq_text, bold=True, align="center", indent=False))
            continue

        # Blockquote / Note / Placeholder
        if stripped.startswith("> "):
            callout_text = stripped[2:].strip()
            body_xml.append(build_paragraph(callout_text, indent=False))
            continue

        # Bullet List Items
        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = "•  " + stripped[2:].strip()
            body_xml.append(build_paragraph(item_text, indent=False, align="both"))
            continue
        
        # Numbered List Items
        if re.match(r'^\d+\.\s+', stripped):
            body_xml.append(build_paragraph(stripped, indent=False, align="both"))
            continue

        # Normal Paragraph with first-line indent
        body_xml.append(build_paragraph(stripped, indent=True, align="both"))

    # Flush any remaining table
    if in_table and table_rows:
        body_xml.append(build_table(table_rows))

    # PENS Standard A4 Section Properties
    sect_pr = """<w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="2268" w:right="1701" w:bottom="1701" w:left="2268" w:header="708" w:footer="708" w:gutter="0"/>
      <w:cols w:space="708"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>"""
    body_xml.append(sect_pr)

    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W_NS}"><w:body>{"".join(body_xml)}</w:body></w:document>'

def generate_docx():
    print(f"Reading markdown source from: {MD_PATH}")
    if not MD_PATH.exists():
        raise FileNotFoundError(f"Source markdown {MD_PATH} not found!")

    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_content = f.read()

    print("Converting markdown elements to OpenXML WordProcessingML...")
    document_xml = convert_markdown_to_docx_body(md_content)
    content_types_xml = create_content_types_xml()
    root_rels_xml = create_root_rels_xml()
    doc_rels_xml = create_document_rels_xml()
    settings_xml = create_settings_xml()
    styles_xml = create_styles_xml()

    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Packing OpenXML archive into: {DOCX_PATH}")

    with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types_xml)
        docx.writestr("_rels/.rels", root_rels_xml)
        docx.writestr("word/_rels/document.xml.rels", doc_rels_xml)
        docx.writestr("word/settings.xml", settings_xml)
        docx.writestr("word/styles.xml", styles_xml)
        docx.writestr("word/document.xml", document_xml)

    size_kb = os.path.getsize(DOCX_PATH) / 1024
    print(f"SUCCESS: Generated {DOCX_PATH} ({size_kb:.2f} KB)")

if __name__ == "__main__":
    generate_docx()
