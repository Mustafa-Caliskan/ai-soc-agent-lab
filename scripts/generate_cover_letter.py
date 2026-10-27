"""
Script to generate a publication-ready formal Cover Letter for Computers and Informatics (C&I):
1. docs/CI_COVER_LETTER.docx
2. docs/CI_COVER_LETTER.md
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def build_cover_letter():
    doc = docx.Document()
    
    # A4 Page setup with standard 2.5 cm margins
    for s in doc.sections:
        s.page_width = Cm(21.0)
        s.page_height = Cm(29.7)
        s.top_margin = Cm(2.5)
        s.bottom_margin = Cm(2.5)
        s.left_margin = Cm(2.5)
        s.right_margin = Cm(2.5)
        
    def add_p(text="", bold_prefix=None, space_after=6, space_before=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(11)
            r_pre.bold = True
        if text:
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
        return p

    # Header / Date
    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_date.paragraph_format.space_after = Pt(14)
    r_date = p_date.add_run("Date: 26 October 2026")
    r_date.font.name = 'Times New Roman'
    r_date.font.size = Pt(10.5)

    # Recipient
    p_rec = doc.add_paragraph()
    p_rec.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_rec.paragraph_format.space_after = Pt(14)
    r_rec = p_rec.add_run(
        "To: The Editorial Board and Editor-in-Chief\n"
        "Computers and Informatics (C&I)\n"
        "DergiPark Academic Publishing, Türkiye\n"
        "e-ISSN: 2757-8259 | Web: https://dergipark.org.tr/en/pub/ci"
    )
    r_rec.font.name = 'Times New Roman'
    r_rec.font.size = Pt(10.5)
    r_rec.bold = True

    # Subject Line
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_sub.paragraph_format.space_after = Pt(12)
    p_sub.paragraph_format.space_before = Pt(4)
    r_sub = p_sub.add_run("SUBJECT: Submission of Original Research Article — \"NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models\"")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(11)
    r_sub.bold = True

    # Salutation
    add_p("Dear Editor-in-Chief and Esteemed Members of the Editorial Board,", space_after=8, align=WD_ALIGN_PARAGRAPH.LEFT)

    # Body Paragraph 1: Submission statement
    add_p("On behalf of my co-author Prof. Dr. Ali Hakan IŞIK and myself, I am pleased to submit our original research manuscript entitled \"NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models\" for consideration for publication as a Research Article in Computers and Informatics (C&I).")

    # Body Paragraph 2: Core Motivation & Novelty
    add_p("In this paper we show that locally deployed and API-served LLMs disclose secrets embedded in their system prompts, that a non-trivial share of this disclosure occurs only in the reasoning channel and is therefore invisible to output-only inspection, and that a six-stage peripheral gateway removes the leak without touching the model. This is significant because enterprises increasingly delegate operational credentials to LLM assistants while measuring safety on the final response alone.")

    add_p("As Large Language Models (LLMs) are rapidly integrated into production environments—such as autonomous workflow agents and retrieval-augmented generation (RAG)—securing natural language interfaces against prompt injection, jailbreaking, and confidential data exfiltration has become a pressing software engineering challenge. Existing commercial and academic guardrails remain predominantly English-centric, fail to address sophisticated non-Latin and steganographic evasion vectors, and exhibit significant performance collapse on non-translated low-resource queries. Furthermore, our pre-registered audit of the legacy out-of-distribution (OOD) suite found that 89.25% of its items name a public training repository in their source field and 8.7% share at least one verbatim 8-gram with our training corpus, which is why the evaluation set was rebuilt on a source-disjoint basis.")

    # Body Paragraph 3: Key Technical Contributions
    add_p("In this work, we propose NeuralShield, a gateway of six stages and five defensive controls (L0 structural normaliser, L1 sub-millisecond deterministic regex, L2 12-language mmBERT-base classifier, L3 OR-Gate arbiter, L4 target model, and L5 dual-stream egress DLP). NeuralShield runs entirely on commodity dual-thread CPU hardware with a median latency of ~50.6 ms (FP32 ONNX runtime), delivering high throughput without requiring expensive GPU infrastructure. Key scientific highlights include:", bold_prefix="Key Contributions & Findings: ")

    # Bullet points
    add_p("On a source-disjoint fair 12-language benchmark (N=2,849), NeuralShield demonstrates statistical parity in Macro-F1 with a commercial guardrail (Patronus Wolf Defender: 84.86% vs. 84.23%, overlapping 95% cluster-bootstrap confidence intervals), while achieving higher recall on native non-translated corpora (+34.4 pp on native Turkish; AUC 0.890 vs. 0.631 on native Cyrillic Russian).", bold_prefix="• Source-Disjoint Fair Parity: ")
    add_p("Empirical red-teaming across 19 distinct model checkpoints (from 1.5B edge models to Tier-2 enterprise models, Tier-3 flagship models on an Enterprise NVIDIA H200 Supercomputing Cluster, three reasoning models, and two additional API models in a native Turkish suite) blocked all 101 curated in-domain attacks, driving attack success rates (ASR) from up to 40.59% (Mistral-7B-v0.3) to flat 0.00%.", bold_prefix="• 14-Model Empirical Red-Teaming: ")
    add_p("We document the phenomenon of 'Silent Chain-of-Thought Exfiltration', showing that flagship reasoning models (Gemma-4-31B and Qwen3.8-Flash-Next) achieve 0.00% user-facing ASR but verbalize confidential system canary secrets verbatim in 66.34% and 14.85% of internal reasoning traces—creating a critical exfiltration vector for SSE streaming architectures that is completely neutralized by NeuralShield's dual-stream egress DLP.", bold_prefix="• Discovery of Silent CoT Exfiltration: ")
    add_p("Full-sample (N=101) paired McNemar tests find no statistically significant quantization effect (4-bit NF4 vs. uncompressed FP16 exhibit overlapping CIs, p=0.804 on Llama-3.1-8B), while demonstrating that aggressive system prompt hardening leaves 16.83% residual leakage and also produces 1.67% benign canary leakage on legitimate user traffic.", bold_prefix="• Full-Pool Paired Ablations: ")

    # Body Paragraph 4: Fit for C&I
    add_p("We believe this manuscript is ideally suited for Computers and Informatics, as it addresses core intersections of computer science, applied machine learning, software security, and computational engineering. The work presents both statistical evaluation (cluster-bootstrap resampling, exact McNemar tests, Wilson score intervals) and practical systems engineering validated under real-world operational constraints.")

    # Declarations
    add_p("In submitting this manuscript, we formally declare that:", bold_prefix="Author Declarations: ", space_after=4)
    add_p("1. The manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere in any language.\n"
          "2. The submission has been reviewed and approved by all authors, and tacit or explicit permission has been obtained from the responsible authorities at Burdur Mehmet Akif Ersoy University.\n"
          "3. The authors declare no competing financial interests or personal relationships that could have influenced the work.\n"
          "4. All code artifacts, trained ONNX models, benchmark datasets and evaluation harnesses have been open-sourced and archived on GitHub (https://github.com/Mustafa-Caliskan/ai-soc-agent-lab) to support reproducibility.\n"
          "5. Blind review requirements have been fully respected: author names and affiliations have been strictly omitted from the main manuscript (docs/NeuralShield_CI_Manuscript.docx) and provided separately in the Title Page (docs/Title_Page.docx).",
          space_after=12)

    # Sign-off
    p_close = doc.add_paragraph()
    p_close.paragraph_format.space_before = Pt(8)
    p_close.paragraph_format.space_after = Pt(4)
    r_close = p_close.add_run("Please address all correspondence concerning this manuscript to me at 2211404051@ogr.mehmetakif.edu.tr.\n\nThank you very much for your time, consideration, and management of the peer-review process.\n\nSincerely yours,")
    r_close.font.name = 'Times New Roman'
    r_close.font.size = Pt(11)

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(12)
    p_sig.paragraph_format.space_after = Pt(2)
    r_sig = p_sig.add_run(
        "Mustafa ÇALIŞKAN (Corresponding Author)\n"
        "Department of Computer Engineering, Faculty of Engineering\n"
        "Burdur Mehmet Akif Ersoy University\n"
        "15030 Burdur, Türkiye\n"
        "Email: 2211404051@ogr.mehmetakif.edu.tr\n"
        "ORCID: 0009-0004-3861-7628\n\n"
        "On behalf of:\n"
        "Prof. Dr. Ali Hakan IŞIK (Co-Author & Academic Advisor)\n"
        "Email: ahakan@mehmetakif.edu.tr | ORCID: 0000-0003-3561-9375"
    )
    r_sig.font.name = 'Times New Roman'
    r_sig.font.size = Pt(10.5)

    os.makedirs("docs", exist_ok=True)
    doc.save("docs/CI_COVER_LETTER.docx")
    print("Successfully built: docs/CI_COVER_LETTER.docx")

    # Also build markdown version
    md_content = """# Cover Letter to the Editorial Board of Computers and Informatics (C&I)

**Date:** 26 October 2026  
**To:** The Editorial Board and Editor-in-Chief  
*Computers and Informatics* (C&I), DergiPark Academic Publishing  
e-ISSN: 2757-8259 | https://dergipark.org.tr/en/pub/ci  

**SUBJECT: Submission of Original Research Article — "NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models"**

Dear Editor-in-Chief and Esteemed Members of the Editorial Board,

On behalf of my co-author Prof. Dr. Ali Hakan IŞIK and myself, I am pleased to submit our original research manuscript entitled **"NeuralShield: A Multilingual Multi-Layer Security Gateway Against Prompt Injection and Data Exfiltration in Large Language Models"** for consideration for publication as a Research Article in *Computers and Informatics* (C&I).

In this paper we show that locally deployed and API-served LLMs disclose secrets embedded in their system prompts, that a non-trivial share of this disclosure occurs only in the reasoning channel and is therefore invisible to output-only inspection, and that a six-stage peripheral gateway removes the leak without touching the model. This is significant because enterprises increasingly delegate operational credentials to LLM assistants while measuring safety on the final response alone.

### Research Motivation and Novelty
As Large Language Models (LLMs) are rapidly integrated into production environments—such as autonomous workflow agents and retrieval-augmented generation (RAG)—securing natural language interfaces against prompt injection, jailbreaking, and confidential data exfiltration has become a pressing software engineering challenge. Existing commercial and academic guardrails remain predominantly English-centric, fail to address sophisticated non-Latin and steganographic evasion vectors, and exhibit significant performance collapse on non-translated low-resource queries. Our pre-registered audit of the legacy out-of-distribution (OOD) suite found that 89.25% of its items name a public training repository in their source field and 8.7% share at least one verbatim 8-gram with our training corpus, which is why the evaluation set was rebuilt on a source-disjoint basis.

### Key Contributions and Findings
In this work, we propose NeuralShield, a gateway of six stages and five defensive controls (L0 structural normaliser, L1 sub-millisecond deterministic regex, L2 12-language mmBERT-base classifier, L3 OR-Gate arbiter, L4 target model, and L5 dual-stream egress DLP). NeuralShield runs entirely on commodity dual-thread CPU hardware with a median latency of ~50.6 ms (FP32 ONNX runtime), delivering high throughput without requiring expensive GPU infrastructure. Key scientific highlights include:
- **Source-Disjoint Fair Parity:** On a source-disjoint fair 12-language benchmark ($N=2,849$), NeuralShield demonstrates statistical parity in Macro-F1 with a commercial guardrail (Patronus Wolf Defender: 84.86% vs. 84.23%, overlapping 95% cluster-bootstrap confidence intervals), while achieving higher recall on native non-translated corpora (+34.4 pp on native Turkish; AUC 0.890 vs. 0.631 on native Cyrillic Russian).
- **19-Checkpoint Empirical Red-Teaming:** Empirical red-teaming across 19 distinct model checkpoints (from 1.5B edge models to Tier-2 enterprise models, Tier-3 flagship models on an Enterprise NVIDIA H200 Supercomputing Cluster, three reasoning models, and two additional API models in a native Turkish suite) blocked all 101 curated in-domain attacks, driving attack success rates (ASR) from up to 40.59% (Mistral-7B-v0.3) to flat 0.00%.
- **Discovery of Silent CoT Exfiltration:** We document the phenomenon of "Silent Chain-of-Thought Exfiltration", showing that flagship reasoning models (Gemma-4-31B and Qwen3.8-Flash-Next) achieve 0.00% user-facing ASR but verbalize confidential system canary secrets verbatim in 66.34% and 14.85% of internal reasoning traces—creating a critical exfiltration vector for SSE streaming architectures that is completely neutralized by NeuralShield's dual-stream egress DLP.
- **Full-Pool Paired Ablations:** Full-sample ($N=101$) paired McNemar tests find no statistically significant quantization effect (4-bit NF4 vs. uncompressed FP16 exhibit overlapping CIs, $p=0.804$ on Llama-3.1-8B), while demonstrating that aggressive system prompt hardening leaves 16.83% residual leakage and also produces 1.67% benign canary leakage on legitimate user traffic.

### Relevance to Computers and Informatics
We believe this manuscript is ideally suited for *Computers and Informatics*, as it addresses core intersections of computer science, applied machine learning, software security, and computational engineering. The work presents both statistical evaluation (cluster-bootstrap resampling, exact McNemar tests, Wilson score intervals) and practical systems engineering validated under real-world operational constraints.

### Author Declarations
In submitting this manuscript, we formally declare that:
1. The manuscript represents original work that has not been published previously and is not under consideration for publication elsewhere in any language.
2. The submission has been reviewed and approved by all authors, and permission has been obtained from the responsible authorities at Burdur Mehmet Akif Ersoy University.
3. The authors declare no competing financial interests or personal relationships that could have influenced the work.
4. All code artifacts, trained ONNX models, benchmark datasets and evaluation harnesses have been open-sourced and archived on GitHub (`https://github.com/Mustafa-Caliskan/ai-soc-agent-lab`). Per-item JSON outputs are released for every suite reported in Tables 1-6 and 8-10; the native Turkish suite of Table 7 is a pilot whose per-item artefacts are not released, and the SSE deployment is documented as an observational case study.
5. Blind review requirements have been fully respected: author names and affiliations have been strictly omitted from the main manuscript (`docs/NeuralShield_CI_Manuscript.docx`) and provided separately in the Title Page (`docs/Title_Page.docx`).

Please address all correspondence concerning this manuscript to me at 2211404051@ogr.mehmetakif.edu.tr.

Thank you very much for your time, consideration, and management of the peer-review process.

Sincerely yours,

**Mustafa ÇALIŞKAN** (Corresponding Author)  
Department of Computer Engineering, Faculty of Engineering  
Burdur Mehmet Akif Ersoy University, 15030 Burdur, Türkiye  
Email: 2211404051@ogr.mehmetakif.edu.tr | ORCID: 0009-0004-3861-7628  

*On behalf of:*  
**Prof. Dr. Ali Hakan IŞIK** (Co-Author & Academic Advisor)  
Email: ahakan@mehmetakif.edu.tr | ORCID: 0000-0003-3561-9375  
"""
    with open("docs/CI_COVER_LETTER.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Successfully built: docs/CI_COVER_LETTER.md")

if __name__ == "__main__":
    build_cover_letter()
