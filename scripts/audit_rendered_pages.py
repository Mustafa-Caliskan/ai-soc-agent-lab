"""
Layout audit for the C&I submission package.

Verifies, through Word COM plus PyMuPDF:
  1. the masked manuscript renders to exactly 17 pages;
  2. all 10 tables are present and none is split across a page boundary;
  3. no orphan heading or dangling table caption sits at the bottom of a page;
  4. the PDF is exported to docs/NeuralShield_CI_Manuscript.pdf.

Exit code is non-zero when a hard criterion fails, so the check can gate a commit.
"""

import os
import shutil
import sys

import fitz
import win32com.client

EXPECTED_PAGES = 17
EXPECTED_TABLES = 10
WD_STAT_PAGES = 2
WD_ACTIVE_END_PAGE = 3
WD_FORMAT_PDF = 17


def audit():
    docx_path = os.path.abspath("docs/NeuralShield_CI_Manuscript.docx")
    pdf_path = os.path.abspath("docs/NeuralShield_CI_Manuscript.pdf")
    mirror_path = os.path.abspath("docs/audit_screenshots/manuscript_rendered.pdf")

    if not os.path.exists(docx_path):
        print(f"FAIL: missing {docx_path}")
        return 2

    for stale in (pdf_path, mirror_path):
        if os.path.exists(stale):
            os.remove(stale)

    print("Rendering PDF from DOCX via Word...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    failures = []
    try:
        doc = word.Documents.Open(docx_path, ReadOnly=True)
        pages = int(doc.ComputeStatistics(WD_STAT_PAGES))
        n_tables = int(doc.Tables.Count)

        print(f"Word page count : {pages}")
        print(f"Word table count: {n_tables} (including front-matter layout tables)")

        if pages != EXPECTED_PAGES:
            failures.append(f"page count {pages} != {EXPECTED_PAGES}")

        # Content tables are preceded by a "Table N." caption; the front-matter
        # layout blocks start with the masked-author or citation marker.
        content_tables = []
        for idx in range(1, n_tables + 1):
            tbl = doc.Tables(idx)
            head = tbl.Rows(1).Range.Text.strip()
            if head.startswith("[Masked") or head.startswith("Cite this paper"):
                continue
            content_tables.append(tbl)

        print(f"Numbered content tables: {len(content_tables)}")
        if len(content_tables) != EXPECTED_TABLES:
            failures.append(
                f"content table count {len(content_tables)} != {EXPECTED_TABLES}")

        print("\n=== TABLE SPLIT CHECK ===")
        for idx, tbl in enumerate(content_tables, start=1):
            first_page = int(tbl.Rows(1).Range.Information(WD_ACTIVE_END_PAGE))
            last_page = int(tbl.Rows(tbl.Rows.Count).Range.Information(WD_ACTIVE_END_PAGE))
            status = "OK" if first_page == last_page else "SPLIT"
            if first_page != last_page:
                failures.append(f"table {idx} spans pages {first_page}-{last_page}")
            print(f"  Table {idx:2d}: pages {first_page}-{last_page}  [{status}]")

        doc.SaveAs(pdf_path, FileFormat=WD_FORMAT_PDF)
        doc.SaveAs(mirror_path, FileFormat=WD_FORMAT_PDF)
        doc.Close(False)
    finally:
        word.Quit()

    if os.path.exists(pdf_path):
        src = fitz.open(pdf_path)
        print(f"\nExported PDF: {pdf_path} ({src.page_count} pages)")
        if src.page_count != EXPECTED_PAGES:
            failures.append(f"exported PDF has {src.page_count} pages")
        src.close()

    if not os.path.exists(mirror_path):
        failures.append("audit mirror PDF was not produced")
    else:
        os.makedirs(os.path.dirname(mirror_path), exist_ok=True)
        if not os.path.exists(pdf_path):
            shutil.copyfile(mirror_path, pdf_path)

    doc = fitz.open(mirror_path)
    print(f"=== PAGE-BY-PAGE AUDIT ({doc.page_count} pages) ===")
    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        first_few = " | ".join(lines[1:3]) if len(lines) > 1 else "[EMPTY]"
        last_few = " | ".join(lines[-2:]) if lines else "[EMPTY]"
        imgs = page.get_images()
        print(f"\n[PAGE {i+1:02d}] (Lines: {len(lines)}, Images: {len(imgs)})")
        print(f"  Start: {first_few[:100]}")
        print(f"  End:   {last_few[:100]}")

        for line in lines[-2:]:
            if (line.startswith(("1. ", "2. ", "3. ", "4. ", "5. ", "2.", "3.", "APPENDIX"))
                    and len(line) < 70):
                print(f"  >>> WARNING: potential orphan heading: '{line}'")
                failures.append(f"orphan heading on page {i+1}: {line[:40]}")
            if line.startswith("Table ") and len(line) < 100 and "." in line[:12]:
                print(f"  >>> WARNING: table caption at page bottom: '{line}'")
                failures.append(f"dangling caption on page {i+1}")

    print("\n=== RESULT ===")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("PASS: 17 pages, 10 unsplit tables, PDF exported.")
    return 0


if __name__ == "__main__":
    sys.exit(audit())
