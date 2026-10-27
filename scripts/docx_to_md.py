# -*- coding: utf-8 -*-
"""DOCX -> MD donusturucu (tek yonlu, her zaman senkron)."""
import sys, os, re
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\Mustafa\OneDrive\Masaüstü\Akademik_yayın"

SRC = os.path.join(R, "docs", "NeuralShield_CI_Manuscript.docx")
OUT = os.path.join(R, "docs", "CI_MANUSCRIPT_EN.md")

doc = Document(SRC)
body = doc.element.body
lines = []
table_idx = 0
para_map = {id(p._element): p for p in doc.paragraphs}
tbl_map = {id(t._element): t for t in doc.tables}

lines.append("<!-- AUTO-GENERATED from NeuralShield_CI_Manuscript.docx by scripts/docx_to_md.py.")
lines.append("     Do not edit by hand: edit scripts/generate_ci_docx.py and re-run both. -->")
lines.append("")

for child in body.iterchildren():
    if child.tag == qn("w:p"):
        p = para_map.get(id(child))
        if p is None:
            continue
        t = p.text.strip()
        if not t:
            continue
        st = p.style.name if p.style else "Normal"
        # baslik seviyeleri
        if st.startswith("Heading"):
            lvl = int(re.search(r"(\d)", st).group(1))
            lines.append("#" * (lvl + 1) + " " + t)
        else:
            # Table/Figure caption italik
            if re.match(r"^(Table|Figure)\s*\d+\.", t):
                lines.append("*" + t + "*")
            else:
                lines.append(t)
        lines.append("")
    elif child.tag == qn("w:tbl"):
        tbl = tbl_map.get(id(child))
        if tbl is None:
            continue
        rows = []
        for r in tbl.rows:
            cells = [c.text.strip().replace("\n", " ").replace("|", "\\|") for c in r.cells]
            # tekrar eden birlestirilmis hucreleri sadelestir
            rows.append(cells)
        if not rows:
            continue
        w = max(len(r) for r in rows)
        rows = [r + [""] * (w - len(r)) for r in rows]
        lines.append("| " + " | ".join(rows[0]) + " |")
        lines.append("|" + "|".join(["---"] * w) + "|")
        for r in rows[1:]:
            lines.append("| " + " | ".join(r) + " |")
        lines.append("")
        table_idx += 1

txt = "\n".join(lines) + "\n"
open(OUT, "w", encoding="utf-8").write(txt)
print("MD yeniden uretildi:", OUT)
print("  satir:", len(lines), "| tablo:", table_idx, "| karakter:", len(txt))
